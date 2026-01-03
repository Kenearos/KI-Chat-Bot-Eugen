"""
Tests for utility classes: MentionDetector and Logger
"""
import pytest
import logging
from utils import MentionDetector, Logger


# Parameterized test data
MENTION_TEST_CASES = [
    # (message, bot_name, expected_result, description)
    ("@Eugen hello", "Eugen", True, "at-mention"),
    ("@eugen hello", "Eugen", True, "at-mention lowercase"),
    ("@EUGEN hello", "Eugen", True, "at-mention uppercase"),
    ("Eugen: what's up?", "Eugen", True, "colon format"),
    ("Eugen! hey", "Eugen", True, "exclamation format"),
    ("Eugen? are you there", "Eugen", True, "question format"),
    ("Eugen, help me", "Eugen", True, "comma format"),
    ("Eugen. listen", "Eugen", True, "period format"),
    ("Hey Eugen how are you", "Eugen", True, "mention in middle"),
    ("Is Eugen online?", "Eugen", True, "mention as word"),
    ("Eugene is different", "Eugen", False, "name as substring of longer word should fail"),
    ("Eugenics is a topic", "Eugen", False, "false positive check"),
    ("Regular message", "Eugen", False, "no mention"),
    ("@kenearosmd hi", "kenearosmd", True, "long name at-mention"),
    ("@kene hi", "kenearosmd", True, "nickname 4 chars"),
    ("@kenearos hi", "kenearosmd", True, "nickname 8 chars"),
    ("kenearosmd: what", "kenearosmd", True, "long name colon"),
    ("kene: what", "kenearosmd", True, "nickname colon"),
]

GREETING_TEST_CASES = [
    # (message, expected_ambiguous, description)
    ("hi", True, "simple hi"),
    ("Hi", True, "capitalized Hi"),
    ("HI", True, "uppercase HI"),
    ("hello", True, "hello"),
    ("hallo", True, "German hallo"),
    ("hey there", True, "hey there"),
    ("moin", True, "German moin"),
    ("servus", True, "German servus"),
    ("wie gehts", True, "German wie gehts"),
    ("wie geht's", True, "German with apostrophe"),
    ("alles klar", True, "German alles klar"),
    ("how are you", True, "English how are you"),
    ("everything ok", True, "English everything ok"),
    ("@Eugen hi", False, "clear mention not ambiguous"),
    ("Eugen: hello", False, "clear mention not ambiguous"),
    ("Just a message", False, "not a greeting"),
    ("high score", False, "hi in word should not match"),
]

CONTENT_EXTRACTION_CASES = [
    # (message, bot_name, expected_content, description)
    ("@Eugen what's the weather?", "Eugen", "what's the weather?", "at-mention extraction"),
    ("Eugen: tell me more", "Eugen", "tell me more", "colon extraction"),
    ("Eugen, help please", "Eugen", "help please", "comma extraction"),
    ("what's up Eugen", "Eugen", "what's up", "mention at end"),
    ("@Eugen", "Eugen", "", "only mention"),
    ("Eugen", "Eugen", "", "only name"),
    ("@kene what's up", "kenearosmd", "what's up", "nickname extraction"),
    ("", "Eugen", "", "empty message"),
]


class TestMentionDetector:
    """Test MentionDetector functionality"""

    @pytest.mark.parametrize("message,bot_name,expected,description", MENTION_TEST_CASES)
    def test_mention_detection_comprehensive(self, message, bot_name, expected, description):
        """Parameterized test for comprehensive mention detection coverage"""
        detector = MentionDetector(bot_name)
        result = detector.is_mentioned(message)
        assert result == expected, f"Failed for case: {description}"

    @pytest.mark.parametrize("message,expected,description", GREETING_TEST_CASES)
    def test_ambiguous_greeting_comprehensive(self, message, expected, description):
        """Parameterized test for comprehensive greeting detection"""
        detector = MentionDetector("Eugen")
        result = detector.is_ambiguous_greeting(message)
        assert result == expected, f"Failed for case: {description}"

    @pytest.mark.parametrize("message,bot_name,expected_content,description", CONTENT_EXTRACTION_CASES)
    def test_content_extraction_comprehensive(self, message, bot_name, expected_content, description):
        """Parameterized test for comprehensive content extraction"""
        detector = MentionDetector(bot_name)
        result = detector.extract_content(message)
        assert result.strip() == expected_content.strip(), f"Failed for case: {description}"

    def test_init_generates_nicknames(self):
        """Test that nicknames are generated from bot name"""
        detector = MentionDetector("kenearosmd")
        assert "kene" in detector.nicknames
        assert "kenearos" in detector.nicknames

    def test_init_short_name_generates_partial_nicknames(self):
        """Test nickname generation with shorter names"""
        detector = MentionDetector("Eugen")
        # Only 5 chars, so only first 4 chars nickname
        assert "Euge" in detector.nicknames

    def test_mention_with_at_symbol(self):
        """Test detection of @mention format"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("@Eugen what's up?")
        assert detector.is_mentioned("Hey @Eugen can you help?")
        assert detector.is_mentioned("@eugen") # case insensitive

    def test_mention_with_colon(self):
        """Test detection of name: format"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("Eugen: what do you think?")
        assert detector.is_mentioned("eugen: hello") # case insensitive

    def test_mention_with_punctuation(self):
        """Test detection with various punctuation"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("Eugen! Hey there!")
        assert detector.is_mentioned("Eugen? Are you there?")
        assert detector.is_mentioned("Eugen, can you help?")
        assert detector.is_mentioned("Eugen. Listen up")

    def test_mention_at_start(self):
        """Test detection of name at message start"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("Eugen what's the weather?")

    def test_mention_anywhere_as_whole_word(self):
        """Test detection of name as whole word anywhere"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("Hey Eugen how are you?")
        assert detector.is_mentioned("Is Eugen online?")

    def test_no_false_positive_partial_match(self):
        """Test that partial matches don't trigger detection"""
        detector = MentionDetector("Eugen")
        # "Eugene" contains "Eugen" but shouldn't match due to word boundary
        assert not detector.is_mentioned("Eugene is a different name")

    def test_nickname_detection(self):
        """Test that nicknames are detected"""
        detector = MentionDetector("kenearosmd")
        assert detector.is_mentioned("@kene what's up?")
        assert detector.is_mentioned("kenearos: hello")

    def test_case_insensitive_detection(self):
        """Test case insensitivity"""
        detector = MentionDetector("Eugen")
        assert detector.is_mentioned("EUGEN")
        assert detector.is_mentioned("eugen")
        assert detector.is_mentioned("EuGeN")

    def test_empty_message_returns_false(self):
        """Test that empty messages return False"""
        detector = MentionDetector("Eugen")
        assert not detector.is_mentioned("")
        assert not detector.is_mentioned(None)

    def test_no_mention_returns_false(self):
        """Test messages without mentions return False"""
        detector = MentionDetector("Eugen")
        assert not detector.is_mentioned("Just a regular message")
        assert not detector.is_mentioned("Nothing to see here")

    def test_ambiguous_greeting_detection(self):
        """Test detection of ambiguous greetings"""
        detector = MentionDetector("Eugen")
        assert detector.is_ambiguous_greeting("hi")
        assert detector.is_ambiguous_greeting("Hi")
        assert detector.is_ambiguous_greeting("hello")
        assert detector.is_ambiguous_greeting("hallo")
        assert detector.is_ambiguous_greeting("hey there")
        assert detector.is_ambiguous_greeting("moin")
        assert detector.is_ambiguous_greeting("servus")

    def test_ambiguous_greeting_german(self):
        """Test German greetings"""
        detector = MentionDetector("Eugen")
        assert detector.is_ambiguous_greeting("wie gehts")
        assert detector.is_ambiguous_greeting("wie geht's")
        assert detector.is_ambiguous_greeting("alles klar")

    def test_ambiguous_greeting_english(self):
        """Test English greetings"""
        detector = MentionDetector("Eugen")
        assert detector.is_ambiguous_greeting("how are you")
        assert detector.is_ambiguous_greeting("everything ok")

    def test_ambiguous_greeting_not_if_mentioned(self):
        """Test that clear mentions don't count as ambiguous"""
        detector = MentionDetector("Eugen")
        assert not detector.is_ambiguous_greeting("@Eugen hi")
        assert not detector.is_ambiguous_greeting("Eugen: hello")

    def test_ambiguous_greeting_empty_message(self):
        """Test ambiguous greeting with empty message"""
        detector = MentionDetector("Eugen")
        assert not detector.is_ambiguous_greeting("")
        assert not detector.is_ambiguous_greeting(None)

    def test_extract_content_removes_at_mention(self):
        """Test content extraction removes @mention"""
        detector = MentionDetector("Eugen")
        assert detector.extract_content("@Eugen what's up?") == "what's up?"
        assert detector.extract_content("@eugen hello") == "hello"

    def test_extract_content_removes_name_with_colon(self):
        """Test content extraction removes name: format"""
        detector = MentionDetector("Eugen")
        assert detector.extract_content("Eugen: what's the weather?") == "what's the weather?"
        assert detector.extract_content("eugen, help me") == "help me"

    def test_extract_content_removes_name_at_start(self):
        """Test content extraction removes name at start"""
        detector = MentionDetector("Eugen")
        assert detector.extract_content("Eugen what's up?") == "what's up?"

    def test_extract_content_removes_name_at_end(self):
        """Test content extraction removes name at end"""
        detector = MentionDetector("Eugen")
        result = detector.extract_content("what's up Eugen")
        assert result.strip() == "what's up"

    def test_extract_content_removes_nickname(self):
        """Test content extraction removes nicknames"""
        detector = MentionDetector("kenearosmd")
        assert detector.extract_content("@kene what's up?") == "what's up?"
        assert detector.extract_content("kenearos: hello") == "hello"

    def test_extract_content_empty_message(self):
        """Test content extraction with empty message"""
        detector = MentionDetector("Eugen")
        assert detector.extract_content("") == ""
        assert detector.extract_content(None) == ""

    def test_extract_content_only_mention(self):
        """Test content extraction when message is only the mention"""
        detector = MentionDetector("Eugen")
        assert detector.extract_content("@Eugen") == ""
        assert detector.extract_content("Eugen") == ""

    def test_extract_content_preserves_other_content(self):
        """Test that extraction doesn't remove legitimate content"""
        detector = MentionDetector("Eugen")
        # Should not remove "Eugene" from content
        result = detector.extract_content("@Eugen tell me about Eugene")
        assert "Eugene" in result


class TestLogger:
    """Test Logger functionality"""

    def _flush_logger(self, logger):
        """Helper to flush logger handlers"""
        for handler in logger.main_logger.handlers:
            handler.flush()
        for handler in logger.api_logger.handlers:
            handler.flush()

    def test_logger_creates_log_directory(self, temp_dir):
        """Test that logger creates log directory"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        assert log_dir.exists()

    def test_logger_creates_main_log_file(self, temp_dir):
        """Test that main log file is created"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.info("test message")
        self._flush_logger(logger)
        main_log = log_dir / "eugen.log"
        assert main_log.exists()

    def test_logger_creates_api_log_file(self, temp_dir):
        """Test that API log file is created"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.api_call("test", "model", 5)
        self._flush_logger(logger)
        api_log = log_dir / "api_debug.log"
        assert api_log.exists()

    def test_logger_info_writes_message(self, temp_dir):
        """Test that info messages are written"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.info("test info message")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "test info message" in content
        assert "INFO" in content

    def test_logger_error_writes_message(self, temp_dir):
        """Test that error messages are written"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.error("test error message")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "test error message" in content
        assert "ERROR" in content

    def test_logger_warning_writes_message(self, temp_dir):
        """Test that warning messages are written"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.warning("test warning message")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "test warning message" in content
        assert "WARNING" in content

    def test_logger_debug_mode_writes_debug(self, temp_dir):
        """Test that debug messages are written in debug mode"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.debug("test debug message")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "test debug message" in content
        assert "DEBUG" in content

    def test_logger_non_debug_mode_skips_debug(self, temp_dir):
        """Test that debug messages are not written when debug_mode=False"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.debug("test debug message")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        # Debug messages shouldn't appear in INFO level logging
        assert "test debug message" not in content

    def test_logger_api_call_logging(self, temp_dir):
        """Test API call logging"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.api_call("https://api.test.com", "sonar-pro", 10)
        self._flush_logger(logger)

        api_log = log_dir / "api_debug.log"
        content = api_log.read_text()
        assert "API CALL" in content
        assert "sonar-pro" in content
        assert "10" in content

    def test_logger_api_response_logging(self, temp_dir):
        """Test API response logging"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.api_response(200, 75, 1.234, "Test response content")
        self._flush_logger(logger)

        api_log = log_dir / "api_debug.log"
        content = api_log.read_text()
        assert "API RESPONSE" in content
        assert "200" in content
        assert "75" in content
        assert "1.23" in content
        assert "Test response" in content

    def test_logger_api_error_logging(self, temp_dir):
        """Test API error logging"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.api_error(401, "Unauthorized access")
        self._flush_logger(logger)

        api_log = log_dir / "api_debug.log"
        content = api_log.read_text()
        assert "API ERROR" in content
        assert "401" in content
        assert "Unauthorized" in content

    def test_logger_chat_message_in_debug_mode(self, temp_dir):
        """Test chat message logging in debug mode"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.chat_message("testuser", "Hello world!")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "CHAT" in content
        assert "testuser" in content
        assert "Hello world!" in content

    def test_logger_chat_message_not_in_non_debug_mode(self, temp_dir):
        """Test chat message not logged when debug_mode=False"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=False)
        logger.chat_message("testuser", "Hello world!")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "Hello world!" not in content

    def test_logger_bot_response_in_debug_mode(self, temp_dir):
        """Test bot response logging in debug mode"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.bot_response("testuser", "Here's my response")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text()
        assert "BOT RESPONSE" in content
        assert "testuser" in content
        assert "Here's my response" in content

    def test_logger_unicode_support(self, temp_dir):
        """Test that logger handles German/Unicode characters"""
        log_dir = temp_dir / "logs"
        logger = Logger(log_dir=str(log_dir), debug_mode=True)
        logger.info("Äpfel, Öle, Über, ß")
        self._flush_logger(logger)

        main_log = log_dir / "eugen.log"
        content = main_log.read_text(encoding='utf-8')
        assert "Äpfel" in content
        assert "Öle" in content
        assert "Über" in content
        assert "ß" in content

    def test_logger_reuses_existing_handlers(self, temp_dir):
        """Test that logger doesn't create duplicate handlers"""
        log_dir = temp_dir / "logs"

        # Create first logger instance to set up handlers
        Logger(log_dir=str(log_dir), debug_mode=True)
        main_logger_1 = logging.getLogger("eugen_main")
        handler_count_1 = len(main_logger_1.handlers)

        # Create second logger with same settings - should not add handlers
        Logger(log_dir=str(log_dir), debug_mode=True)
        main_logger_2 = logging.getLogger("eugen_main")
        handler_count_2 = len(main_logger_2.handlers)

        # Underlying logger should have the same number of handlers (reused, not duplicated)
        assert handler_count_1 == handler_count_2
        assert handler_count_1 > 0  # But should have at least one handler
