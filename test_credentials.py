"""
Credential Testing Utility for Eugen Bot
Tests and validates Twitch OAuth tokens and Perplexity API keys
"""
import asyncio
import socket
import sys
import os
import httpx
from dotenv import load_dotenv


class Colors:
    """ANSI color codes"""
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


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


async def test_twitch_token(token, nickname):
    """
    Test Twitch OAuth token with detailed diagnostics

    Args:
        token (str): OAuth token
        nickname (str): Bot nickname

    Returns:
        bool: True if valid
    """
    print_header("TESTING TWITCH CREDENTIALS")

    # Check token format
    if not token:
        print_error("Token is empty!")
        print_info("Get a token from: https://twitchtokengenerator.com")
        return False

    if not token.startswith("oauth:"):
        print_warning(f"Token doesn't start with 'oauth:' (got: {token[:10]}...)")
        print_info("Token should look like: oauth:abcd1234...")
        return False

    print_info(f"Token format: ✓ Starts with 'oauth:'")
    print_info(f"Token length: {len(token)} characters")
    print_info(f"Bot nickname: {nickname}")

    # Test IRC connection
    print_info("\nConnecting to Twitch IRC (irc.chat.twitch.tv:6667)...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)

            # Connect
            try:
                sock.connect(('irc.chat.twitch.tv', 6667))
                print_success("Connected to IRC server")
            except socket.timeout:
                print_error("Connection timed out!")
                print_info("Check your internet connection and firewall settings")
                return False
            except Exception as e:
                print_error(f"Connection failed: {e}")
                return False

            # Send authentication
            print_info("Sending authentication...")
            sock.send(f"PASS {token}\r\n".encode())
            sock.send(f"NICK {nickname}\r\n".encode())

            # Wait for response
            response = ""
            try:
                response = sock.recv(2048).decode()
            except socket.timeout:
                print_error("No response from server (timeout)")
                return False

            # Parse response
            print_info(f"\nServer response received ({len(response)} bytes)")

            if "Login authentication failed" in response:
                print_error("AUTHENTICATION FAILED!")
                print_info("\nPossible reasons:")
                print(f"  1. Token is expired or invalid")
                print(f"  2. Token doesn't match the bot nickname '{nickname}'")
                print(f"  3. Account that generated the token is banned/restricted")
                print_info("\nHow to fix:")
                print(f"  → Go to: https://twitchtokengenerator.com")
                print(f"  → Make sure you're logged into Twitch as '{nickname}'")
                print(f"  → Generate a new 'Bot Chat Token'")
                print(f"  → Update TWITCH_OAUTH_TOKEN in .env")
                return False

            if ":tmi.twitch.tv 001" in response or "Welcome" in response:
                print_success("AUTHENTICATION SUCCESSFUL!")
                print_info(f"Bot '{nickname}' can connect to Twitch IRC")
                return True

            # Ambiguous response
            print_warning("Received unexpected response:")
            for line in response.split('\r\n'):
                if line:
                    print(f"  {line[:100]}")

            # If we got this far without clear failure, consider it success
            if "authentication failed" not in response.lower():
                print_success("Authentication appears successful (no error detected)")
                return True

            return False

    except Exception as e:
        print_error(f"Error testing Twitch token: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_perplexity_key(api_key, model="sonar-pro"):
    """
    Test Perplexity API key with model fallback

    Args:
        api_key (str): Perplexity API key
        model (str): Model to test (will fallback to 'sonar' if needed)

    Returns:
        tuple: (success, recommended_model)
    """
    print_header("TESTING PERPLEXITY API")

    # Check key format
    if not api_key:
        print_error("API key is empty!")
        print_info("Get a key from: https://www.perplexity.ai/settings/api")
        return False, None

    if not api_key.startswith("pplx-"):
        print_warning(f"API key doesn't start with 'pplx-' (got: {api_key[:10]}...)")
        print_info("Key should look like: pplx-abc123...")

    print_info(f"API key format: Starts with '{api_key[:5]}...'")
    print_info(f"API key length: {len(api_key)} characters")

    # Test with different models
    models_to_test = [model]
    if model != "sonar":
        models_to_test.append("sonar")

    for test_model in models_to_test:
        print_info(f"\nTesting with model: {test_model}")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    json={
                        "model": test_model,
                        "messages": [{"role": "user", "content": "Say 'test successful' and nothing else"}],
                        "max_tokens": 10
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )

                print_info(f"Response status: {response.status_code}")

                if response.status_code == 200:
                    print_success(f"API KEY VALID with model '{test_model}'!")

                    # Try to parse response
                    try:
                        data = response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0]["message"]["content"]
                            print_info(f"Test response: '{content}'")
                    except Exception:
                        pass

                    return True, test_model

                elif response.status_code == 401:
                    print_error("API key is INVALID (401 Unauthorized)")
                    print_info("\nHow to fix:")
                    print(f"  → Go to: https://www.perplexity.ai/settings/api")
                    print(f"  → Generate a new API key")
                    print(f"  → Update PERPLEXITY_API_KEY in .env")
                    return False, None

                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        print_warning(f"400 Bad Request: {error_msg}")

                        # Check if it's a model access issue
                        if "model" in error_msg.lower():
                            print_info(f"Model '{test_model}' not available on your plan")
                            if test_model != models_to_test[-1]:
                                print_info("Trying fallback model...")
                                continue
                        else:
                            print_info(f"Error details: {error_msg}")
                    except Exception:
                        print_warning(f"400 Bad Request (couldn't parse error)")

                    # If this was the last model, fail
                    if test_model == models_to_test[-1]:
                        print_error("All models failed!")
                        return False, None

                elif response.status_code == 429:
                    print_error("Rate limited! Too many requests.")
                    print_info("Wait a few minutes and try again")
                    return False, None

                else:
                    print_warning(f"Unexpected status code: {response.status_code}")
                    try:
                        print_info(f"Response: {response.text[:200]}")
                    except Exception:
                        pass

                    # Try next model if available
                    if test_model != models_to_test[-1]:
                        continue

                    return False, None

        except httpx.TimeoutException:
            print_error("Request timed out!")
            print_info("Check your internet connection")
            return False, None
        except Exception as e:
            print_error(f"Error testing API: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    return False, None


async def main():
    """Main test runner"""
    print(f"""
{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════════════════════════════╗
║              EUGEN BOT - CREDENTIAL VALIDATOR                      ║
║              Tests Twitch & Perplexity Credentials                 ║
╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}
""")

    # Load .env file
    if not os.path.exists('.env'):
        print_error("No .env file found!")
        print_info("Please run: python setup_wizard.py")
        sys.exit(1)

    load_dotenv()

    # Get credentials
    twitch_token = os.getenv('TWITCH_OAUTH_TOKEN', '')
    twitch_nickname = os.getenv('TWITCH_BOT_NICKNAME', '')
    twitch_channel = os.getenv('TWITCH_CHANNEL', '')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY', '')
    perplexity_model = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')

    print_info("Loaded configuration from .env:")
    print(f"  • Bot Nickname: {twitch_nickname}")
    print(f"  • Channel: {twitch_channel}")
    print(f"  • Model: {perplexity_model}")

    # Test credentials
    results = {}

    # Test Twitch
    results['twitch'] = await test_twitch_token(twitch_token, twitch_nickname)

    # Test Perplexity
    results['perplexity'], recommended_model = await test_perplexity_key(perplexity_key, perplexity_model)

    # Final summary
    print_header("VALIDATION SUMMARY")

    print(f"Twitch IRC:      {'✓ PASS' if results['twitch'] else '✗ FAIL'}")
    print(f"Perplexity API:  {'✓ PASS' if results['perplexity'] else '✗ FAIL'}")

    if recommended_model and recommended_model != perplexity_model:
        print_warning(f"\nRecommendation: Update PERPLEXITY_MODEL to '{recommended_model}' in .env")

    if all(results.values()):
        print_success("\n🎉 All credentials valid! Bot is ready to run.")
        print_info("Start the bot with: python chatbot.py")
        sys.exit(0)
    else:
        print_error("\n❌ Some credentials are invalid. Please fix and re-test.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
