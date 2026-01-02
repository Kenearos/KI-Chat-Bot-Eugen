"""
Configuration Management for Eugen Bot
Loads settings from .env and config.json
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Manages bot configuration from environment variables and config files"""

    def __init__(self, env_file=".env", config_file="data/config.json"):
        # Load .env file
        load_dotenv(env_file)

        # Twitch Configuration
        self.twitch_token = os.getenv("TWITCH_OAUTH_TOKEN", "")
        self.twitch_channel = os.getenv("TWITCH_CHANNEL", "")
        self.bot_name = os.getenv("TWITCH_BOT_NICKNAME", "Eugen")

        # Perplexity Configuration
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "450"))

        # Bot Behavior
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.auto_reconnect = os.getenv("AUTO_RECONNECT", "true").lower() == "true"
        self.reconnect_delay = int(os.getenv("RECONNECT_DELAY", "10"))

        # Data Configuration
        self.data_dir = os.getenv("DATA_DIR", "data/conversations")
        self.log_dir = os.getenv("LOG_DIR", "logs")
        self.context_retention_hours = int(os.getenv("CONTEXT_RETENTION_HOURS", "1"))

        # Additional settings from config.json
        self.config_file = config_file
        self._load_json_config()

    def _load_json_config(self):
        """Load additional settings from config.json if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # Override or extend settings from JSON
                    for key, value in config_data.items():
                        if not hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")

    def save_to_json(self):
        """Save current configuration to config.json"""
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
        config_data = {
            "bot_name": self.bot_name,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "debug_mode": self.debug_mode,
            "auto_reconnect": self.auto_reconnect,
            "reconnect_delay": self.reconnect_delay,
            "context_retention_hours": self.context_retention_hours
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def is_configured(self):
        """Check if all required settings are present"""
        required = [
            self.twitch_token,
            self.twitch_channel,
            self.perplexity_key,
            self.bot_name
        ]
        return all(required) and self.twitch_token.startswith("oauth:")

    def get_system_prompt(self):
        """Returns the system prompt for the AI"""
        return """Du bist Kene (auch bekannt als Kenearos oder Keneraosmd), ein Twitch-Streamer.

WICHTIG: Du antwortest ALS Kene selbst, nicht als separater Bot. Sprich in der ersten Person ("Ich...", "Mein Setup...", etc.)

Über dich:
- Streamer, Botter (Automatisierung/Coding), Gamer
- 3D-Druck mit Bambu X1C und H2C
- Themen: Gaming (WoW, Elden Ring, Gamedev), 3D-Druck, Coding/Bots, Linux, Home Automation
- Humor: Vielseitig - Sarkasmus, Dad-Jokes, Gaming-Memes, Spaß & Fun
- Chat-Stil: Locker und direkt, aber technisch detailliert wenn nötig

Politische Haltung:
- Linkspolitisch eingestellt
- Argumentierst klar gegen rechte Positionen, Rechtsmitte und Nazis
- Bei politischen Themen: Klare Kante, aber sachlich bleiben

Chat-Verhalten:
- Antworte kurz (2-3 Sätze max für Twitch-Chat)
- Authentisch und natürlich, wie Kene selbst sprechen würde
- Bei Tech/3D-Druck-Fragen: Gerne detaillierter mit konkreten Tipps
- Beziehe dich auf frühere Chat-Nachrichten wenn möglich
- Ehrlich sagen wenn du etwas nicht weißt

Wichtig: Du bist Kene's AI-Assistent der für ihn antwortet - handle im Chat wie er es tun würde."""
