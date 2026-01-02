"""
Setup Wizard for Eugen Twitch Bot
Interactive configuration tool for first-time setup
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import set_key, load_dotenv


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


async def validate_twitch_token(token, channel):
    """
    Validate Twitch OAuth token by attempting IRC connection

    Args:
        token (str): OAuth token
        channel (str): Channel name

    Returns:
        bool: True if valid
    """
    import socket

    if not token.startswith("oauth:"):
        print_error("Token muss mit 'oauth:' beginnen!")
        return False

    try:
        print_info("Validiere Twitch-Verbindung...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('irc.chat.twitch.tv', 6667))

        # Send authentication
        sock.send(f"PASS {token}\r\n".encode())
        sock.send(f"NICK testbot\r\n".encode())

        response = sock.recv(1024).decode()
        sock.close()

        if "Login authentication failed" in response:
            print_error("Twitch OAuth Token ist ungültig!")
            return False

        print_success("Twitch-Verbindung erfolgreich!")
        return True

    except Exception as e:
        print_warning(f"Konnte Twitch-Verbindung nicht testen: {e}")
        print_info("Fahre trotzdem fort - bitte später manuell prüfen!")
        return True


async def validate_perplexity_key(api_key):
    """
    Validate Perplexity API key with test request

    Args:
        api_key (str): Perplexity API key

    Returns:
        bool: True if valid
    """
    import httpx

    try:
        print_info("Validiere Perplexity API-Key...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 200:
                print_success("Perplexity API-Key ist gültig!")
                return True
            elif response.status_code == 401:
                print_error("Perplexity API-Key ist ungültig!")
                return False
            else:
                print_warning(f"Unerwartete Antwort: {response.status_code}")
                print_info("Fahre trotzdem fort - bitte später manuell prüfen!")
                return True

    except Exception as e:
        print_warning(f"Konnte Perplexity API nicht testen: {e}")
        print_info("Fahre trotzdem fort - bitte später manuell prüfen!")
        return True


def create_env_file(config):
    """
    Create or update .env file with configuration

    Args:
        config (dict): Configuration dictionary
    """
    env_file = ".env"

    # Create .env if it doesn't exist
    if not os.path.exists(env_file):
        Path(env_file).touch()

    # Write all config values
    for key, value in config.items():
        set_key(env_file, key, value)

    print_success(f".env Datei erstellt/aktualisiert!")


def create_directories():
    """Create necessary directories for bot operation"""
    directories = [
        "data",
        "data/conversations",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print_success("Verzeichnisse erstellt!")


def get_input(prompt, default=None, required=True, secret=False):
    """
    Get user input with validation

    Args:
        prompt (str): Input prompt
        default (str): Default value
        required (bool): Whether input is required
        secret (bool): Whether to hide input (for passwords)

    Returns:
        str: User input
    """
    import getpass

    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "

    while True:
        if secret:
            value = getpass.getpass(prompt_text)
        else:
            value = input(prompt_text)

        # Use default if provided and input is empty
        if not value and default:
            return default

        # Check if required
        if required and not value:
            print_error("Dieses Feld ist erforderlich!")
            continue

        return value


async def run_wizard():
    """Main wizard flow"""

    # Welcome
    print_header("🤖 EUGEN BOT SETUP WIZARD 🤖")
    print("Willkommen beim Setup-Assistenten für deinen Twitch-Bot!")
    print("Dieser Wizard führt dich durch die Erstkonfiguration.\n")

    print_info("Du benötigst:")
    print("  1. Einen Twitch OAuth Token")
    print("  2. Deinen Twitch Channel-Namen")
    print("  3. Einen Perplexity API Key")
    print()

    input("Drücke ENTER um zu starten...")

    # Configuration dictionary
    config = {}

    # Step 1: Twitch Configuration
    print_header("SCHRITT 1: TWITCH KONFIGURATION")

    print_info("Twitch OAuth Token generieren:")
    print("  → Gehe zu: https://twitchtokengenerator.com")
    print("  → Wähle 'Bot Chat Token'")
    print("  → Authorisiere und kopiere das 'oauth:...' Token")
    print()

    while True:
        token = get_input("Twitch OAuth Token", secret=True, required=True)
        if not token.startswith("oauth:"):
            print_warning("Token sollte mit 'oauth:' beginnen. Füge ich hinzu...")
            token = f"oauth:{token}"

        config['TWITCH_OAUTH_TOKEN'] = token
        break

    config['TWITCH_CHANNEL'] = get_input(
        "Twitch Channel Name (ohne #)",
        default="keneraosmd",
        required=True
    )

    # Add # if not present
    if not config['TWITCH_CHANNEL'].startswith('#'):
        config['TWITCH_CHANNEL'] = f"#{config['TWITCH_CHANNEL']}"

    config['TWITCH_BOT_NICKNAME'] = get_input(
        "Bot Nickname",
        default="Eugen",
        required=True
    )

    # Validate Twitch
    if not await validate_twitch_token(config['TWITCH_OAUTH_TOKEN'], config['TWITCH_CHANNEL']):
        retry = input("\nTrotzdem fortfahren? (j/n): ")
        if retry.lower() != 'j':
            print_error("Setup abgebrochen!")
            return False

    # Step 2: Perplexity Configuration
    print_header("SCHRITT 2: PERPLEXITY API")

    print_info("Perplexity API Key erhalten:")
    print("  → Gehe zu: https://www.perplexity.ai/settings/api")
    print("  → Erstelle einen neuen API Key")
    print("  → Kopiere den Key (beginnt mit 'pplx-...')")
    print()

    while True:
        api_key = get_input("Perplexity API Key", secret=True, required=True)
        config['PERPLEXITY_API_KEY'] = api_key

        if await validate_perplexity_key(api_key):
            break

        retry = input("\nErneut versuchen? (j/n): ")
        if retry.lower() != 'j':
            print_error("Setup abgebrochen!")
            return False

    # Step 3: Advanced Settings
    print_header("SCHRITT 3: ERWEITERTE EINSTELLUNGEN")

    print("Möchtest du erweiterte Einstellungen konfigurieren?")
    advanced = input("(j/n, default: n): ").lower() == 'j'

    if advanced:
        config['PERPLEXITY_MODEL'] = get_input(
            "Perplexity Modell",
            default="sonar-pro"
        )
        config['MAX_TOKENS'] = get_input(
            "Max Tokens pro Antwort",
            default="450"
        )
        config['DEBUG_MODE'] = get_input(
            "Debug Mode aktivieren?",
            default="false"
        )
        config['CONTEXT_RETENTION_HOURS'] = get_input(
            "Context Retention (Stunden)",
            default="1"
        )
    else:
        config['PERPLEXITY_MODEL'] = "sonar-pro"
        config['MAX_TOKENS'] = "450"
        config['DEBUG_MODE'] = "false"
        config['CONTEXT_RETENTION_HOURS'] = "1"

    # Step 4: Create files and directories
    print_header("SCHRITT 4: SETUP ABSCHLIESSEN")

    print_info("Erstelle Konfigurationsdateien...")
    create_env_file(config)
    create_directories()

    # Final summary
    print_header("✅ SETUP ERFOLGREICH!")

    print(f"{Colors.OKGREEN}Deine Konfiguration:{Colors.ENDC}")
    print(f"  Channel: {config['TWITCH_CHANNEL']}")
    print(f"  Bot Name: {config['TWITCH_BOT_NICKNAME']}")
    print(f"  Modell: {config['PERPLEXITY_MODEL']}")
    print(f"  Max Tokens: {config['MAX_TOKENS']}")
    print()

    print_info("Nächste Schritte:")
    print("  1. Starte den Bot mit: python chatbot.py")
    print("  2. Der Bot verbindet sich mit Twitch")
    print("  3. Erwähne den Bot im Chat mit '@Eugen' oder 'Eugen:'")
    print()

    print_success("Viel Spaß mit deinem Bot! 🚀")
    return True


def main():
    """Main entry point"""
    try:
        # Check if already configured
        if os.path.exists('.env'):
            load_dotenv()
            if os.getenv('TWITCH_OAUTH_TOKEN') and os.getenv('PERPLEXITY_API_KEY'):
                print_warning(".env Datei existiert bereits!")
                reconfigure = input("Möchtest du die Konfiguration überschreiben? (j/n): ")
                if reconfigure.lower() != 'j':
                    print_info("Setup abgebrochen. Nutze die bestehende Konfiguration.")
                    return

        # Run async wizard
        success = asyncio.run(run_wizard())

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print_warning("Setup abgebrochen!")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fehler während des Setups: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
