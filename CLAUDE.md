# CLAUDE.md - Project Guide for Claude Code

## Project Overview

**Eugen** is an intelligent Twitch chat bot for gaming and 3D printing topics. The bot uses the Perplexity Sonar API for AI-powered responses and features persistent conversation memory per user.

### Core Functionality
- Responds when mentioned in chat (@Eugen, Eugen:, etc.)
- Maintains conversation history per user (max 25 messages)
- Integrates with Perplexity API for intelligent responses
- Provides a GUI dashboard for live monitoring

### Primary Topics
- **Gaming**: World of Warcraft, Elden Ring, Gamedev
- **3D Printing**: Prusa i3, Bambu, Creality
- **Tech**: Python, Linux, Home Automation

## Tech Stack

- **Language**: Python 3.9+ (recommended 3.11+)
- **AI Provider**: Perplexity API (sonar-pro model)
- **Chat Protocol**: Twitch IRC
- **GUI Framework**: FreeSimpleGUI 5.1+ (community fork, no license required)
- **Platform**: Windows-native (no Linux tools required)

## Project Structure

```
eugen/
├── chatbot.py              # Main entry point
├── setup_wizard.py         # Interactive setup wizard
├── test_credentials.py     # Credential validation tool
├── config.py               # Configuration management
├── gui.py                  # Dashboard GUI
├── ai_provider.py          # Perplexity API integration
├── memory.py               # Conversation memory storage
├── utils.py                # Helper functions (MentionDetector, Logger)
├── requirements.txt        # Python dependencies
├── .env                    # Secrets (DO NOT COMMIT)
│
├── data/
│   ├── conversations/      # Per-user chat histories (*.json)
│   └── config.json         # Saved configuration
│
└── logs/
    ├── eugen.log           # Main log file
    └── api_debug.log       # API debug logs
```

## Key Components

### Classes
- `EugenBot` - Main orchestrator for IRC, Memory, AI, and GUI
- `MentionDetector` - Detects bot mentions in chat messages
- `ConversationMemory` - Stores/loads chat history per user
- `PerplexityProvider` - Handles Perplexity API communication
- `Dashboard` - PySimpleGUI-based live monitoring interface
- `Config` - Loads configuration from .env and config.json

### Message Flow
1. Chat message received via IRC
2. MentionDetector checks if bot was addressed
3. ConversationMemory loads user's last 5 messages
4. Prompt built with system prompt + history + current message
5. API call to Perplexity Sonar
6. Response saved to memory and sent to chat
7. Dashboard updated with event

## Development Guidelines

### Dependencies
```
irc==20.1.0
python-dotenv==1.0.0
FreeSimpleGUI==5.1.1
requests==2.31.0
httpx==0.25.0
```

### Environment Variables (.env)
```
TWITCH_OAUTH_TOKEN=oauth:xxxxx
TWITCH_BOT_NICKNAME=Eugen
TWITCH_CHANNEL=#channel_name
PERPLEXITY_API_KEY=pplx-xxxxx
PERPLEXITY_MODEL=sonar-pro
MAX_TOKENS=450
DEBUG_MODE=true
```

### Important Notes
- Never commit .env or files containing API keys
- User conversation files are stored as JSON in data/conversations/
- Context retention is limited to 1 hour by default
- Max tokens for responses: 450 (Twitch chat limit consideration)

## Common Commands

```bash
# Setup virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run interactive setup wizard
python setup_wizard.py

# Test credentials (recommended before first run)
python test_credentials.py

# Run the bot
python chatbot.py
```

## Testing Credentials

Use the credential validator for comprehensive testing:

```bash
python test_credentials.py
```

This tool:
- Tests Twitch OAuth token with IRC authentication
- Validates Perplexity API key and model access
- Provides detailed error diagnostics
- Suggests fixes for common issues
- Automatically tests fallback models (sonar-pro → sonar)

Manual testing:
- **Twitch**: Test IRC connection to irc.chat.twitch.tv:6667
- **Perplexity**: POST to https://api.perplexity.ai/chat/completions with a simple test message

## Error Handling

Common issues:
- Invalid Twitch Token: Regenerate at twitchtokengenerator.com
- Perplexity API 401: Check API key validity and account credits
- IRC Connection Failed: Check firewall rules for port 6667
- Rate Limiting: Built-in auto-retry after 60 seconds

## Language Note

This project's documentation (eugen_claude.md) is in German. The bot is designed for German-speaking Twitch communities but can be adapted for other languages.
