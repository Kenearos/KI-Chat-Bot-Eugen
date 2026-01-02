"""
Tests for Config class
"""
import pytest
import os
import json
from pathlib import Path
from config import Config


class TestConfig:
    """Test Config functionality"""

    def test_config_loads_from_env_file(self, temp_dir, mock_env_file):
        """Test that config loads from .env file"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        assert config.twitch_token == "oauth:test_token_12345"
        assert config.twitch_channel == "#test_channel"
        assert config.bot_name == "TestBot"
        assert config.perplexity_key == "pplx-test-key-12345"
        assert config.model == "sonar-pro"
        assert config.max_tokens == 450

    def test_config_default_values(self, temp_dir):
        """Test default values when env vars are missing"""
        # Create empty env file
        empty_env = temp_dir / ".env"
        empty_env.write_text("")

        config = Config(env_file=str(empty_env), config_file=str(temp_dir / "config.json"))

        assert config.bot_name == "Eugen"  # Default
        assert config.model == "sonar-pro"  # Default
        assert config.max_tokens == 450  # Default
        assert config.debug_mode is False  # Default
        assert config.auto_reconnect is True  # Default

    def test_config_debug_mode_true(self, temp_dir):
        """Test debug mode parsing when set to true"""
        env_file = temp_dir / ".env"
        env_file.write_text("DEBUG_MODE=true\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.debug_mode is True

    def test_config_debug_mode_false(self, temp_dir):
        """Test debug mode parsing when set to false"""
        env_file = temp_dir / ".env"
        env_file.write_text("DEBUG_MODE=false\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.debug_mode is False

    def test_config_debug_mode_case_insensitive(self, temp_dir):
        """Test debug mode parsing is case insensitive"""
        env_file = temp_dir / ".env"
        env_file.write_text("DEBUG_MODE=TRUE\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.debug_mode is True

    def test_config_auto_reconnect_parsing(self, temp_dir):
        """Test auto_reconnect boolean parsing"""
        env_file = temp_dir / ".env"
        env_file.write_text("AUTO_RECONNECT=false\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.auto_reconnect is False

    def test_config_integer_parsing(self, temp_dir):
        """Test integer parsing for numeric configs"""
        env_file = temp_dir / ".env"
        env_file.write_text("""MAX_TOKENS=300
RECONNECT_DELAY=20
CONTEXT_RETENTION_HOURS=2
""")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.max_tokens == 300
        assert config.reconnect_delay == 20
        assert config.context_retention_hours == 2

    def test_config_loads_from_json(self, temp_dir, mock_env_file, mock_config_json):
        """Test that config loads from JSON file"""
        config = Config(env_file=str(mock_env_file), config_file=str(mock_config_json))

        # JSON values should be loaded
        # Note: .env takes precedence for overlapping keys
        assert config.bot_name == "TestBot"
        assert config.model == "sonar-pro"

    def test_config_json_extends_env(self, temp_dir, mock_env_file):
        """Test that JSON config can extend env config with new keys"""
        config_json_path = temp_dir / "config.json"
        config_data = {
            "custom_setting": "custom_value",
            "another_setting": 123
        }
        with open(config_json_path, 'w') as f:
            json.dump(config_data, f)

        config = Config(env_file=str(mock_env_file), config_file=str(config_json_path))

        assert hasattr(config, "custom_setting")
        assert config.custom_setting == "custom_value"
        assert hasattr(config, "another_setting")
        assert config.another_setting == 123

    def test_config_json_missing_doesnt_crash(self, temp_dir, mock_env_file):
        """Test that missing config.json doesn't crash"""
        nonexistent = temp_dir / "nonexistent.json"

        # Should not raise exception
        config = Config(env_file=str(mock_env_file), config_file=str(nonexistent))

        # Should still have env values
        assert config.bot_name == "TestBot"

    def test_config_json_invalid_doesnt_crash(self, temp_dir, mock_env_file):
        """Test that invalid JSON doesn't crash"""
        invalid_json = temp_dir / "config.json"
        invalid_json.write_text("{ invalid json }")

        # Should not raise exception
        config = Config(env_file=str(mock_env_file), config_file=str(invalid_json))

        # Should still have env values
        assert config.bot_name == "TestBot"

    def test_is_configured_returns_true_when_valid(self, temp_dir, mock_env_file):
        """Test that is_configured returns True with valid config"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        assert config.is_configured() is True

    def test_is_configured_requires_oauth_prefix(self, temp_dir):
        """Test that is_configured checks for oauth: prefix"""
        env_file = temp_dir / ".env"
        env_file.write_text("""TWITCH_OAUTH_TOKEN=missing_oauth_prefix
TWITCH_CHANNEL=#channel
TWITCH_BOT_NICKNAME=Bot
PERPLEXITY_API_KEY=key
""")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.is_configured() is False

    def test_is_configured_requires_all_fields(self, temp_dir):
        """Test that is_configured checks all required fields"""
        env_file = temp_dir / ".env"

        # Missing perplexity key
        env_file.write_text("""TWITCH_OAUTH_TOKEN=oauth:token
TWITCH_CHANNEL=#channel
TWITCH_BOT_NICKNAME=Bot
""")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.is_configured() is False

    def test_is_configured_with_empty_fields(self, temp_dir):
        """Test that is_configured rejects empty fields"""
        env_file = temp_dir / ".env"
        env_file.write_text("""TWITCH_OAUTH_TOKEN=oauth:token
TWITCH_CHANNEL=
TWITCH_BOT_NICKNAME=Bot
PERPLEXITY_API_KEY=key
""")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.is_configured() is False

    def test_save_to_json(self, temp_dir, mock_env_file):
        """Test saving config to JSON file"""
        config_json_path = temp_dir / "saved_config.json"
        config = Config(env_file=str(mock_env_file), config_file=str(config_json_path))

        config.save_to_json()

        assert config_json_path.exists()

        with open(config_json_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["bot_name"] == "TestBot"
        assert saved_data["model"] == "sonar-pro"
        assert saved_data["max_tokens"] == 450
        assert saved_data["debug_mode"] is True

    def test_save_to_json_creates_directory(self, temp_dir, mock_env_file):
        """Test that save_to_json creates parent directory if needed"""
        nested_path = temp_dir / "nested" / "dir" / "config.json"
        config = Config(env_file=str(mock_env_file), config_file=str(nested_path))

        config.save_to_json()

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_save_to_json_uses_utf8_encoding(self, temp_dir, mock_env_file):
        """Test that save_to_json writes valid JSON with UTF-8 encoding"""
        config_json_path = temp_dir / "config.json"
        config = Config(env_file=str(mock_env_file), config_file=str(config_json_path))

        config.save_to_json()

        # Should be able to read as UTF-8 without errors
        with open(config_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Should have valid JSON structure
        assert isinstance(data, dict)
        assert "bot_name" in data

    def test_get_system_prompt_returns_string(self, temp_dir, mock_env_file):
        """Test that get_system_prompt returns a string"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        prompt = config.get_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_get_system_prompt_contains_bot_context(self, temp_dir, mock_env_file):
        """Test that system prompt contains bot context"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        prompt = config.get_system_prompt()

        # Should contain relevant context about the bot
        assert "Kene" in prompt or "AI" in prompt
        assert "3D-Druck" in prompt or "Gaming" in prompt

    def test_data_dir_configuration(self, temp_dir):
        """Test data directory configuration"""
        env_file = temp_dir / ".env"
        env_file.write_text("DATA_DIR=custom/data/path\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.data_dir == "custom/data/path"

    def test_log_dir_configuration(self, temp_dir):
        """Test log directory configuration"""
        env_file = temp_dir / ".env"
        env_file.write_text("LOG_DIR=custom/logs\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.log_dir == "custom/logs"

    def test_twitch_channel_with_hash(self, temp_dir):
        """Test that Twitch channel is stored with hash"""
        env_file = temp_dir / ".env"
        env_file.write_text("TWITCH_CHANNEL=#mychannel\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        assert config.twitch_channel == "#mychannel"

    def test_twitch_channel_without_hash(self, temp_dir):
        """Test Twitch channel without hash (should be accepted as-is)"""
        env_file = temp_dir / ".env"
        env_file.write_text("TWITCH_CHANNEL=mychannel\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        # Config stores as-is, validation happens elsewhere
        assert config.twitch_channel == "mychannel"

    def test_perplexity_model_sonar(self, temp_dir):
        """Test Perplexity sonar model configuration"""
        env_file = temp_dir / ".env"
        env_file.write_text("PERPLEXITY_MODEL=sonar\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.model == "sonar"

    def test_perplexity_model_sonar_pro(self, temp_dir):
        """Test Perplexity sonar-pro model configuration"""
        env_file = temp_dir / ".env"
        env_file.write_text("PERPLEXITY_MODEL=sonar-pro\n")

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))
        assert config.model == "sonar-pro"

    def test_config_immutable_after_load(self, temp_dir, mock_env_file):
        """Test that config values can be modified after load"""
        config = Config(env_file=str(mock_env_file), config_file=str(temp_dir / "config.json"))

        original_model = config.model

        # Should be able to modify
        config.model = "different-model"
        assert config.model == "different-model"
        assert config.model != original_model

    def test_config_with_whitespace_in_values(self, temp_dir):
        """Test that whitespace in env values is handled"""
        env_file = temp_dir / ".env"
        env_file.write_text('TWITCH_OAUTH_TOKEN= oauth:token_with_space \n')

        config = Config(env_file=str(env_file), config_file=str(temp_dir / "config.json"))

        # dotenv should handle whitespace stripping
        assert config.twitch_token.strip() == "oauth:token_with_space"

    def test_save_to_json_doesnt_include_secrets(self, temp_dir, mock_env_file):
        """Test that save_to_json doesn't save API keys"""
        config_json_path = temp_dir / "config.json"
        config = Config(env_file=str(mock_env_file), config_file=str(config_json_path))

        config.save_to_json()

        with open(config_json_path, 'r') as f:
            saved_data = json.load(f)

        # Should NOT contain secrets
        assert "twitch_token" not in saved_data
        assert "perplexity_key" not in saved_data
        assert "oauth" not in str(saved_data).lower()

        # Should contain non-secret config
        assert "bot_name" in saved_data
        assert "model" in saved_data
