"""
Integration tests for Eugen Bot
Tests the full workflow and component integration
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from config import Config
from memory import ConversationMemory
from ai_provider import PerplexityProvider
from utils import MentionDetector, Logger


class TestFullWorkflow:
    """Test complete bot workflow integration"""

    @pytest.mark.asyncio
    async def test_mention_to_response_workflow(self, temp_dir, mock_env_file, mock_perplexity_response):
        """Test full workflow: mention detection → memory → API → response"""
        # Setup components
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        memory = ConversationMemory(data_dir=str(temp_dir / "conversations"))
        detector = MentionDetector(config.bot_name)
        ai = PerplexityProvider(api_key=config.perplexity_key, model=config.model)

        # Mock API response
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Simulate user message
            username = "testuser"
            user_message = "@TestBot what's the weather?"

            # 1. Detect mention
            assert detector.is_mentioned(user_message)

            # 2. Extract content
            content = detector.extract_content(user_message)
            assert content == "what's the weather?"

            # 3. Load history
            history = memory.get_user_history(username, limit=5)
            assert len(history) == 0  # First message

            # 4. Build messages for API
            messages = [{"role": "system", "content": config.get_system_prompt()}]
            messages.extend(memory.format_for_prompt(history))
            messages.append({"role": "user", "content": content})

            # 5. Get AI response
            response = await ai.get_response(messages)
            assert response == "This is a test response from the AI."

            # 6. Save to memory
            memory.add_message(username, "user", content)
            memory.add_message(username, "assistant", response)

            # 7. Verify history was saved
            saved_history = memory.get_user_history(username)
            assert len(saved_history) == 2
            assert saved_history[0]["content"] == content
            assert saved_history[1]["content"] == response

    @pytest.mark.asyncio
    async def test_conversation_context_preserved(self, temp_dir, mock_env_file):
        """Test that conversation context is preserved across messages"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        memory = ConversationMemory(data_dir=str(temp_dir / "conversations"))
        ai = PerplexityProvider(api_key=config.perplexity_key)

        username = "testuser"

        # Simulate multiple exchanges
        exchanges = [
            ("user", "What is Python?"),
            ("assistant", "Python is a programming language."),
            ("user", "Tell me more about it"),
            ("assistant", "It's known for readability."),
        ]

        for role, content in exchanges:
            memory.add_message(username, role, content)

        # Verify all messages are stored
        history = memory.get_user_history(username, limit=10)
        assert len(history) == 4
        assert history[0]["content"] == "What is Python?"
        assert history[3]["content"] == "It's known for readability."

        # Verify format for prompt works
        formatted = memory.format_for_prompt(history)
        assert len(formatted) == 4
        assert all("timestamp" not in msg for msg in formatted)

    def test_config_to_components_integration(self, temp_dir, mock_env_file):
        """Test that config properly initializes all components"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        # Create components with config values
        memory = ConversationMemory(
            data_dir=config.data_dir,
            retention_hours=config.context_retention_hours
        )
        ai = PerplexityProvider(
            api_key=config.perplexity_key,
            model=config.model,
            max_tokens=config.max_tokens
        )
        detector = MentionDetector(bot_name=config.bot_name)
        logger = Logger(log_dir=config.log_dir, debug_mode=config.debug_mode)

        # Verify components are properly configured
        assert memory.retention_hours == config.context_retention_hours
        assert ai.model == config.model
        assert ai.max_tokens == config.max_tokens
        assert detector.bot_name == config.bot_name
        assert logger.debug_mode == config.debug_mode

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, temp_dir, mock_env_file):
        """Test that system recovers gracefully from errors"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        memory = ConversationMemory(data_dir=str(temp_dir / "conversations"))
        ai = PerplexityProvider(api_key=config.perplexity_key)

        username = "testuser"

        # Add some history
        memory.add_message(username, "user", "Hello")
        memory.add_message(username, "assistant", "Hi there!")

        # Simulate API failure
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # API call fails
            response = await ai.get_response([{"role": "user", "content": "test"}])
            assert response is None

            # Verify error was tracked
            assert ai.total_errors == 1

        # Verify memory still intact despite API failure
        history = memory.get_user_history(username)
        assert len(history) == 2

    def test_mention_detection_integration_with_nicknames(self, temp_dir, mock_env_file):
        """Test mention detection with generated nicknames"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        detector = MentionDetector(config.bot_name)

        # TestBot should generate "Test" as nickname
        test_messages = [
            ("@TestBot hello", True),
            ("@Test hello", True),
            ("TestBot: what's up?", True),
            ("Test: what's up?", True),
            ("Hey TestBot!", True),
            ("Hey Test!", True),
        ]

        for message, should_match in test_messages:
            assert detector.is_mentioned(message) == should_match

    @pytest.mark.asyncio
    async def test_memory_limit_enforcement_in_workflow(self, temp_dir, mock_env_file):
        """Test that memory limits are enforced during conversation"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        memory = ConversationMemory(
            data_dir=str(temp_dir / "conversations"),
            max_messages=10
        )

        username = "testuser"

        # Add 15 messages (exceeds limit)
        for i in range(15):
            memory.add_message(username, "user", f"Message {i}")

        # Should only keep last 10
        history = memory.get_user_history(username, limit=20)
        assert len(history) == 10
        assert history[0]["content"] == "Message 5"
        assert history[9]["content"] == "Message 14"

    @pytest.mark.asyncio
    async def test_ambiguous_greeting_workflow(self, temp_dir, mock_env_file):
        """Test handling of ambiguous greetings"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))
        detector = MentionDetector(config.bot_name)

        # Ambiguous greetings that should be detected
        ambiguous = ["hi", "hello", "wie gehts"]

        for greeting in ambiguous:
            # Not a clear mention
            assert not detector.is_mentioned(greeting)
            # But is ambiguous
            assert detector.is_ambiguous_greeting(greeting)

        # Clear mentions should not be ambiguous
        clear_mentions = ["@TestBot hi", "TestBot: hello"]

        for mention in clear_mentions:
            assert detector.is_mentioned(mention)
            assert not detector.is_ambiguous_greeting(mention)


class TestComponentInteraction:
    """Test interactions between components"""

    def test_logger_integration_with_memory(self, temp_dir):
        """Test that logger works with memory operations"""
        logger = Logger(log_dir=str(temp_dir / "logs"), debug_mode=True)
        memory = ConversationMemory(
            data_dir=str(temp_dir / "conversations"),
            logger=logger
        )

        # Operations should log to the provided logger
        memory.add_message("testuser", "user", "Test message")

        # Logger should have created log files
        assert (temp_dir / "logs" / "eugen.log").exists()

    @pytest.mark.asyncio
    async def test_logger_integration_with_ai_provider(self, temp_dir, mock_perplexity_response):
        """Test that logger works with AI provider"""
        logger = Logger(log_dir=str(temp_dir / "logs"), debug_mode=True)
        ai = PerplexityProvider(api_key="test-key", logger=logger)

        # Mock API call
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await ai.get_response([{"role": "user", "content": "test"}])

        # Verify log was created
        assert (temp_dir / "logs" / "eugen.log").exists()

    def test_config_validation_workflow(self, temp_dir):
        """Test complete config validation workflow"""
        # Create incomplete config
        incomplete_env = temp_dir / ".env"
        incomplete_env.write_text("TWITCH_BOT_NICKNAME=TestBot\n")

        config = Config(env_file=str(incomplete_env), config_file=str(temp_dir / "config.json"))

        # Should fail validation
        assert not config.is_configured()

        # Create complete config
        complete_env = temp_dir / "complete.env"
        complete_env.write_text("""TWITCH_OAUTH_TOKEN=oauth:test123
TWITCH_CHANNEL=#testchannel
TWITCH_BOT_NICKNAME=TestBot
PERPLEXITY_API_KEY=pplx-test123
""")

        config2 = Config(env_file=str(complete_env), config_file=str(temp_dir / "config.json"))

        # Should pass validation
        assert config2.is_configured()
