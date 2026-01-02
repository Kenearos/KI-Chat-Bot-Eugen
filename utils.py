"""
Utility classes for Eugen Bot
Includes MentionDetector for name recognition and Logger for file logging
"""
import re
import logging
from pathlib import Path
from datetime import datetime


class MentionDetector:
    """Detects if the bot was mentioned in a chat message"""

    def __init__(self, bot_name="Eugen"):
        self.bot_name = bot_name

        # Generate nicknames/partial names from bot_name
        self.nicknames = self._generate_nicknames(bot_name)

        # Create patterns for various mention formats
        # Include bot name and all nicknames
        all_names = [bot_name] + self.nicknames
        self.patterns = []

        for name in all_names:
            self.patterns.extend([
                rf"@{name}\b",  # @name (with word boundary)
                rf"\b{name}[:!?.,]",  # name: name! name? name, name.
                rf"^{name}\b",  # name at start of message
                rf"\b{name}\b",  # name anywhere as whole word
            ])

        # Case-insensitive compilation
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.patterns
        ]

        # Patterns for ambiguous greetings (might be directed at bot)
        self.greeting_patterns = [
            r"^(hi|hey|hallo|hello|servus|moin)(\s|$|\W)",
            r"^(wie\s+geht'?s|wie\s+gehts|how\s+are\s+you)",
            r"^(alles\s+klar|everything\s+ok)",
        ]
        self.compiled_greetings = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.greeting_patterns
        ]

    def _generate_nicknames(self, bot_name):
        """Generate common nicknames from bot name"""
        nicknames = []

        # For kenearosmd, generate: Kene, Kenearos
        if len(bot_name) >= 4:
            nicknames.append(bot_name[:4])  # First 4 chars (Kene)
        if len(bot_name) >= 8:
            nicknames.append(bot_name[:8])  # First 8 chars (Kenearos)

        # Remove duplicates and the full name
        nicknames = [n for n in set(nicknames) if n != bot_name]

        return nicknames

    def is_mentioned(self, message):
        """
        Check if bot was mentioned in message

        Args:
            message (str): Chat message to check

        Returns:
            bool: True if bot was mentioned
        """
        if not message:
            return False

        for pattern in self.compiled_patterns:
            if pattern.search(message):
                return True
        return False

    def is_ambiguous_greeting(self, message):
        """
        Check if message is an ambiguous greeting that might be for the bot

        Args:
            message (str): Chat message to check

        Returns:
            bool: True if message is an ambiguous greeting
        """
        if not message:
            return False

        # Don't check if there's already a clear mention
        if self.is_mentioned(message):
            return False

        for pattern in self.compiled_greetings:
            if pattern.search(message):
                return True
        return False

    def extract_content(self, message):
        """
        Extract message content without the mention

        Args:
            message (str): Original message with mention

        Returns:
            str: Message content without mention prefix
        """
        if not message:
            return ""

        # Remove bot name and nickname mentions from the message
        content = message
        all_names = [self.bot_name] + self.nicknames

        for name in all_names:
            # Remove @mention at start
            content = re.sub(rf"^@{name}\b[,:]?\s*", "", content, flags=re.IGNORECASE)

            # Remove name at start with optional punctuation
            content = re.sub(rf"^{name}\b[,:]?\s*", "", content, flags=re.IGNORECASE)

            # Remove name at end with optional punctuation
            content = re.sub(rf"\s*\b{name}[,!?.]?\s*$", "", content, flags=re.IGNORECASE)

            # Remove name in middle with punctuation
            content = re.sub(rf"\s*\b{name}[,:!?]\s*", " ", content, flags=re.IGNORECASE)

        return content.strip()


class Logger:
    """File-based logger for bot events"""

    def __init__(self, log_dir="logs", debug_mode=False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.debug_mode = debug_mode

        # Setup main logger
        self.main_logger = self._setup_logger(
            "eugen_main",
            self.log_dir / "eugen.log",
            logging.INFO if not debug_mode else logging.DEBUG
        )

        # Setup API debug logger
        self.api_logger = self._setup_logger(
            "eugen_api",
            self.log_dir / "api_debug.log",
            logging.DEBUG
        )

    def _setup_logger(self, name, log_file, level):
        """Setup a logger with file handler"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(level)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Console handler for debug mode
        if self.debug_mode:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    def info(self, message):
        """Log info message"""
        self.main_logger.info(message)

    def debug(self, message):
        """Log debug message"""
        self.main_logger.debug(message)

    def error(self, message):
        """Log error message"""
        self.main_logger.error(message)

    def warning(self, message):
        """Log warning message"""
        self.main_logger.warning(message)

    def api_call(self, endpoint, model, messages_count):
        """Log API call details"""
        self.api_logger.debug(
            f"API CALL | Endpoint: {endpoint} | Model: {model} | Messages: {messages_count}"
        )

    def api_response(self, status_code, tokens_used, response_time, content_preview):
        """Log API response details"""
        self.api_logger.debug(
            f"API RESPONSE | Status: {status_code} | Tokens: {tokens_used} | "
            f"Time: {response_time:.2f}s | Content: {content_preview[:100]}..."
        )

    def api_error(self, status_code, error_message):
        """Log API error"""
        self.api_logger.error(
            f"API ERROR | Status: {status_code} | Error: {error_message}"
        )

    def chat_message(self, username, message):
        """Log chat message"""
        if self.debug_mode:
            self.main_logger.debug(f"CHAT | {username}: {message}")

    def bot_response(self, username, response):
        """Log bot response"""
        if self.debug_mode:
            self.main_logger.debug(f"BOT RESPONSE | To {username}: {response}")
