# Eugen - Intelligent Twitch Chat Bot

An AI-powered Twitch chat bot specializing in Gaming and 3D Printing topics, powered by Perplexity Sonar API.

## Features

- **Smart Name Recognition**: Automatically responds when mentioned (@Eugen, Eugen:, etc.)
- **Persistent Memory**: Maintains conversation history per user (max 25 messages)
- **Context-Aware**: Remembers previous conversations for up to 1 hour
- **Perplexity Integration**: Uses Perplexity Sonar API for intelligent, real-time responses
- **Live Dashboard**: GUI monitoring interface showing all activity in real-time
- **Topics**: Gaming (WoW, Elden Ring), 3D Printing (Prusa, Bambu, Creality), Tech (Python, Linux)

## Quick Start

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- Twitch account for the bot
- Perplexity API key

### Installation

```bash
# Clone the repository
git clone https://github.com/Kenearos/KI-Chat-Bot-Eugen.git
cd KI-Chat-Bot-Eugen

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

#### Option 1: Setup Wizard (Recommended)
Run the interactive setup wizard to configure the bot:
```bash
python setup_wizard.py
```

The wizard will:
- Guide you through getting Twitch OAuth token
- Help you set up Perplexity API key
- Validate your credentials
- Create necessary directories and config files

#### Option 2: Manual Configuration
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```
TWITCH_OAUTH_TOKEN=oauth:your_token_here
TWITCH_BOT_NICKNAME=Eugen
TWITCH_CHANNEL=#your_channel_here
PERPLEXITY_API_KEY=pplx-your_key_here
```

#### Getting API Keys

**Twitch OAuth Token:**
1. Visit [twitchtokengenerator.com](https://twitchtokengenerator.com/)
2. Generate token with `chat:read` and `chat:edit` scopes
3. Copy the token (should start with `oauth:`)

**Perplexity API Key:**
1. Visit [perplexity.ai/api](https://www.perplexity.ai/api)
2. Sign up/Login
3. Generate new API key
4. Copy the key (should start with `pplx-`)

### Running the Bot

```bash
python chatbot.py
```

The dashboard will open automatically showing live activity.

## Usage

Once running, the bot responds when mentioned in Twitch chat:

```
User: @Eugen what's the best class in WoW?
Eugen: @User The best class depends on your playstyle...

User: Eugen, how do I level my 3D printer?
Eugen: @User For bed leveling, start by...
```

## Project Structure

```
eugen/
├── chatbot.py          # Main entry point
├── config.py           # Configuration management
├── gui.py              # Dashboard GUI
├── ai_provider.py      # Perplexity API integration
├── memory.py           # Conversation memory
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── .env               # Your secrets (DO NOT COMMIT)
├── data/
│   └── conversations/ # User chat histories
└── logs/
    ├── eugen.log      # Main log
    └── api_debug.log  # API debug logs
```

## Documentation

- **CLAUDE.md**: Quick reference guide for Claude Code
- **eugen_claude.md**: Detailed German documentation with architecture and implementation details

## Development

The bot is built with:
- Python 3.9+
- Perplexity Sonar API for AI responses
- Twitch IRC for chat integration
- PySimpleGUI for dashboard
- Async/await for concurrent operations

## Troubleshooting

**Bot doesn't respond:**
- Check that .env has correct OAuth token and API key
- Verify bot is in the correct channel
- Check logs/eugen.log for errors

**API errors:**
- Verify Perplexity API key is valid
- Check your API credits at perplexity.ai
- Enable DEBUG_MODE=true in .env for detailed logs

**IRC connection failed:**
- Verify internet connection
- Check firewall settings for port 6667
- Regenerate Twitch OAuth token if expired

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or pull request. 
