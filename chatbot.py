"""
Eugen - Intelligent Twitch Chat Bot
Main entry point and orchestrator
"""
import asyncio
import irc.bot
import irc.strings
import threading
import os
from pathlib import Path

from config import Config
from memory import ConversationMemory
from ai_provider import PerplexityProvider
from gui import Dashboard, SetupWizard
from utils import MentionDetector, Logger


class EugenBot(irc.bot.SingleServerIRCBot):
    """Main bot class - orchestrates IRC, Memory, AI, and GUI"""

    def __init__(self, config):
        """
        Initialize the bot

        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.bot_name = config.bot_name
        self.channel = config.twitch_channel

        # Initialize logger first
        self.logger = Logger(log_dir=config.log_dir, debug_mode=config.debug_mode)

        # Initialize components
        self.memory = ConversationMemory(
            data_dir=config.data_dir,
            retention_hours=config.context_retention_hours,
            logger=self.logger
        )
        self.ai = PerplexityProvider(
            api_key=config.perplexity_key,
            model=config.model,
            max_tokens=config.max_tokens,
            logger=self.logger
        )
        self.detector = MentionDetector(bot_name=self.bot_name)

        # Dashboard (will be initialized in GUI thread)
        self.dashboard = None

        # IRC connection setup
        server = "irc.chat.twitch.tv"
        port = 6667
        nickname = self.bot_name
        token = config.twitch_token

        # Initialize IRC bot
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(server, port, token)],
            nickname,
            nickname
        )

        self.is_running = False
        self.loop = None
        self.loop_ready = threading.Event()  # Signal when event loop is ready

        self.logger.info(f"Bot initialized: {nickname} → {self.channel}")

    def on_welcome(self, connection, event):
        """Called when bot connects to IRC server"""
        self.logger.info("Connected to Twitch IRC")
        if self.dashboard:
            self.dashboard.log_event("info", {"message": "Connected to Twitch IRC"})

        # Request Twitch-specific capabilities
        connection.cap("REQ", ":twitch.tv/membership")
        connection.cap("REQ", ":twitch.tv/tags")
        connection.cap("REQ", ":twitch.tv/commands")

        # Join channel
        connection.join(self.channel)
        self.logger.info(f"Joined channel: {self.channel}")
        if self.dashboard:
            self.dashboard.log_event("info", {"message": f"Joined {self.channel}"})

    def on_pubmsg(self, connection, event):
        """Called when a message is received in chat"""
        # Extract username and message
        username = event.source.nick
        message = event.arguments[0]

        self.logger.chat_message(username, message)
        if self.dashboard:
            self.dashboard.log_event("chat_message", {
                "username": username,
                "content": message
            })

        # Check if bot was mentioned
        if self.detector.is_mentioned(message):
            self.logger.debug(f"Mention detected from {username}")
            if self.dashboard:
                self.dashboard.log_event("mention_detected", {"username": username})

            # Process in async context
            asyncio.run_coroutine_threadsafe(
                self.handle_mention(username, message),
                self.loop
            )

    async def handle_mention(self, username, message):
        """
        Handle a message where bot was mentioned

        Args:
            username (str): User who sent the message
            message (str): Full message content
        """
        # Extract actual content without mention
        content = self.detector.extract_content(message)

        self.logger.debug(f"Extracted content from '{message}': '{content}'")
        if self.dashboard:
            self.dashboard.log_event("info", {"message": f"Content extracted: '{content}'"})

        if not content:
            self.logger.warning(f"Empty content after extraction from: {message}")
            if self.dashboard:
                self.dashboard.log_event("warning", {"message": f"Empty content from: {message}"})
            return

        try:
            # Load user's conversation history
            history = self.memory.get_user_history(username, limit=5)
            self.logger.debug(f"Loaded {len(history)} messages for {username}")

            if self.dashboard:
                self.dashboard.log_event("context_loaded", {
                    "username": username,
                    "count": len(history)
                })

            # Build messages for API
            messages = [{"role": "system", "content": self.config.get_system_prompt()}]

            # Add conversation history
            if history:
                messages.extend(self.memory.format_for_prompt(history))

            # Add current message
            messages.append({"role": "user", "content": content})

            self.logger.api_call("chat.completions", self.config.model, len(messages))
            if self.dashboard:
                self.dashboard.log_event("api_call", {
                    "model": self.config.model,
                    "messages": len(messages)
                })

            # Get AI response
            response = await self.ai.get_response(messages)

            if response:
                # Log and display response
                self.logger.debug(f"Received response: {response[:100]}...")
                if self.dashboard:
                    self.dashboard.log_event("api_response", {"content": response})

                # Save to memory
                self.memory.add_message(username, "user", content)
                self.memory.add_message(username, "assistant", response)

                # Send to chat
                self.send_chat_message(username, response)

            else:
                error_msg = "Sorry, I couldn't process that right now."
                self.logger.error("API call failed")
                if self.dashboard:
                    self.dashboard.log_event("error", {"error": "API call failed"})
                self.send_chat_message(username, error_msg)

        except Exception as e:
            self.logger.error(f"Error handling mention: {str(e)}")
            if self.dashboard:
                self.dashboard.log_event("error", {"error": str(e)})

    def send_chat_message(self, username, response):
        """
        Send a message to chat

        Args:
            username (str): User to address
            response (str): Message content
        """
        # Format message to address user
        message = f"@{username} {response}"

        # Send via IRC
        self.connection.privmsg(self.channel, message)

        self.logger.bot_response(username, response)
        if self.dashboard:
            self.dashboard.log_event("bot_response", {
                "username": username,
                "content": response
            })

    def start(self):
        """Start the bot"""
        self.is_running = True

        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()

        # Start event loop in separate thread
        loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        loop_thread.start()

        # Wait for event loop to be ready before starting IRC bot
        self.logger.debug("Waiting for event loop to be ready...")
        self.loop_ready.wait(timeout=5.0)
        if not self.loop_ready.is_set():
            self.logger.error("Event loop failed to start within timeout")
            raise RuntimeError("Event loop failed to start")
        self.logger.debug("Event loop is ready")

        # Start bot in separate thread
        bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        bot_thread.start()

        # Run dashboard in main thread
        self.dashboard = Dashboard(self)
        self.logger.info("Starting dashboard...")
        self.dashboard.run()

    def _run_event_loop(self):
        """Run the async event loop (called in thread)"""
        asyncio.set_event_loop(self.loop)
        self.logger.debug("Starting event loop...")
        
        # Signal that the loop is ready
        self.loop_ready.set()
        
        try:
            self.loop.run_forever()
        finally:
            # Cleanup pending asyncio tasks and close the loop
            self.logger.debug("Event loop stopped, starting cleanup...")
            try:
                pending = [t for t in asyncio.all_tasks(self.loop) if not t.done()]
                for task in pending:
                    task.cancel()
                if pending:
                    self.loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                # Shutdown async generators
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            except Exception as cleanup_error:
                # Log but do not re-raise to avoid masking original shutdown reason
                self.logger.debug(f"Error during event loop cleanup: {cleanup_error}")
            finally:
                self.loop.close()
                self.logger.debug("Event loop closed")

    def _run_bot(self):
        """Run the IRC bot (called in thread)"""
        try:
            self.logger.info("Starting IRC bot...")
            super().start()
        except Exception as e:
            # Ignore errors related to shutdown (file descriptor issues)
            error_msg = str(e)
            if "file descriptor" in error_msg.lower() and not self.is_running:
                self.logger.debug(f"Shutdown cleanup: {error_msg}")
            else:
                self.logger.error(f"Bot error: {error_msg}")
                if self.dashboard:
                    self.dashboard.log_event("error", {"error": f"Bot crashed: {error_msg}"})

    def stop(self):
        """Stop the bot"""
        self.is_running = False
        self.logger.info("Stopping bot...")
        if self.dashboard:
            self.dashboard.log_event("info", {"message": "Shutting down..."})

        # Safely disconnect from IRC
        try:
            if hasattr(self, 'connection') and self.connection and self.connection.connected:
                self.connection.quit("Bot shutting down")
        except Exception as e:
            self.logger.debug(f"Error during disconnect: {str(e)}")

        # Stop IRC bot
        try:
            self.die()
        except Exception as e:
            self.logger.debug(f"Error during die(): {str(e)}")

        # Stop event loop
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


def check_env_file():
    """Check if .env file exists, if not run setup wizard"""
    env_path = Path(".env")

    if not env_path.exists():
        print("No .env file found. Running setup wizard...")
        wizard = SetupWizard()
        config = wizard.run()

        if config:
            # Create .env file
            with open(".env", "w") as f:
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            print(".env file created successfully!")
            return True
        else:
            print("Setup cancelled. Please create .env manually or run setup again.")
            return False

    return True


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                    EUGEN TWITCH BOT                           ║
║             Gaming & 3D-Druck Chat Assistant                  ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Check for configuration
    if not check_env_file():
        return

    # Load configuration
    config = Config()

    if not config.is_configured():
        print("ERROR: Configuration incomplete!")
        print("Please check your .env file or run setup wizard again.")
        print("Delete .env to run setup wizard on next start.")
        return

    print(f"Bot Name: {config.bot_name}")
    print(f"Channel: {config.twitch_channel}")
    print(f"Model: {config.model}")
    print(f"Debug Mode: {config.debug_mode}")
    print("\nStarting bot...\n")

    # Create and start bot
    bot = EugenBot(config)
    bot.start()


if __name__ == "__main__":
    main()
