# Eugen Bot - Troubleshooting Guide

Quick reference for diagnosing and fixing common issues with the Eugen Twitch bot.

## Quick Start Diagnostic Tool

**Before anything else**, run the credential validator:

```bash
python test_credentials.py
```

This tool will:
- Test your Twitch OAuth token
- Validate your Perplexity API key
- Check model availability (sonar-pro vs sonar)
- Provide specific error messages
- Suggest exact fixes

---

## Common Error Messages

### 1. Twitch IRC Authentication Failed

**Error Output:**
```
IRC EVENT: privnotice | Source: tmi.twitch.tv | Args: ['Login authentication failed']
```

**Causes:**
- Token is expired or invalid
- Token doesn't match the bot nickname
- Bot account is banned/suspended

**Solution:**

1. **Verify Bot Nickname Match**
   - If `TWITCH_BOT_NICKNAME=Eugen`, you must generate the token while logged into Twitch as `Eugen`
   - Token and bot nickname MUST match the same account

2. **Generate New Token**
   ```
   1. Go to: https://twitchtokengenerator.com
   2. Log into Twitch as the bot account
   3. Select "Bot Chat Token"
   4. Copy the full token (including oauth: prefix)
   5. Update .env file:
      TWITCH_OAUTH_TOKEN=oauth:your_new_token_here
   ```

3. **Test the Token**
   ```bash
   python test_credentials.py
   ```

### 2. Perplexity API 400 Bad Request

**Error Output:**
```
⚠ Unerwartete Antwort: 400
```

**Causes:**
- API key doesn't have access to `sonar-pro` model
- Invalid request format
- Model not available on your plan

**Solution:**

1. **Use Model Fallback**
   - The setup wizard automatically tries `sonar` if `sonar-pro` fails
   - Manually update `.env`:
     ```
     PERPLEXITY_MODEL=sonar
     ```

2. **Verify API Key**
   ```bash
   python test_credentials.py
   ```

3. **Check API Credits**
   - Go to: https://www.perplexity.ai/settings/api
   - Verify your account has credits
   - Check API key is active

### 3. Perplexity API 401 Unauthorized

**Error Output:**
```
✗ Perplexity API-Key ist ungültig (401 Unauthorized)
```

**Causes:**
- Invalid API key
- API key was revoked
- Typo in `.env` file

**Solution:**

1. **Generate New API Key**
   ```
   1. Go to: https://www.perplexity.ai/settings/api
   2. Create new API key
   3. Copy the key (starts with pplx-)
   4. Update .env:
      PERPLEXITY_API_KEY=pplx-your_new_key_here
   ```

2. **Verify No Extra Spaces**
   - Check `.env` file has no spaces around the `=` sign
   - Format: `PERPLEXITY_API_KEY=pplx-abc123` (no spaces)

### 4. Bot Doesn't Respond in Chat

**Symptoms:**
- Bot connects successfully
- Bot joins channel
- But doesn't respond to mentions

**Checklist:**

1. **Verify Bot is Mentioned Correctly**
   ```
   ✓ @Eugen how are you?
   ✓ Eugen: tell me about WoW
   ✓ Eugen, what's new?
   ✗ eugen (lowercase doesn't work)
   ```

2. **Check Debug Logs**
   ```bash
   tail -f logs/eugen.log
   ```
   Look for:
   - `Mention detected from {user}`
   - `API call to Perplexity`
   - Any error messages

3. **Enable Debug Mode**
   ```
   DEBUG_MODE=true
   ```
   Restart the bot and check logs again

4. **Test Credentials**
   ```bash
   python test_credentials.py
   ```

### 5. Connection Reset by Peer

**Error Output:**
```
IRC EVENT: disconnect | Args: ['Connection reset by peer']
```

**Causes:**
- Network interruption
- Firewall blocking port 6667
- Invalid authentication (see #1)

**Solution:**

1. **Check Firewall**
   - Allow outbound connections on port 6667
   - Try temporarily disabling firewall to test

2. **Verify Internet Connection**
   ```bash
   ping irc.chat.twitch.tv
   ```

3. **Check OAuth Token** (most common cause)
   ```bash
   python test_credentials.py
   ```

### 6. Rate Limiting / API Quota Exceeded

**Error Output:**
```
429 Too Many Requests
```

**Causes:**
- Too many API calls in short time
- Perplexity API quota exceeded

**Solution:**

1. **Check API Usage**
   - Go to: https://www.perplexity.ai/settings/api
   - View usage and limits

2. **Reduce Request Frequency**
   - Consider implementing cooldowns
   - Limit responses to specific users

3. **Wait and Retry**
   - Wait a few minutes
   - Restart the bot

---

## Diagnostic Commands

### Check Configuration
```bash
cat .env
```

### View Recent Logs
```bash
tail -n 50 logs/eugen.log
```

### View API Debug Logs
```bash
tail -n 50 logs/api_debug.log
```

### Test Credentials
```bash
python test_credentials.py
```

### Run Setup Wizard Again
```bash
python setup_wizard.py
```

---

## Getting Help

### Before Asking for Help

1. Run `python test_credentials.py`
2. Check `logs/eugen.log`
3. Enable `DEBUG_MODE=true` and restart
4. Review this troubleshooting guide

### Information to Include

When reporting issues, include:
- Error messages from logs
- Output of `python test_credentials.py`
- Contents of `.env` (REDACT secrets!)
- Python version: `python --version`
- OS: Windows/Linux/Mac

### Resources

- **GitHub Issues**: https://github.com/Kenearos/KI-Chat-Bot-Eugen/issues
- **Twitch Token Generator**: https://twitchtokengenerator.com
- **Perplexity API**: https://www.perplexity.ai/settings/api

---

## Quick Reference

### File Locations
- Configuration: `.env`
- Main log: `logs/eugen.log`
- API debug: `logs/api_debug.log`
- Conversations: `data/conversations/`

### Required Credentials
- Twitch OAuth Token (starts with `oauth:`)
- Twitch Bot Nickname (must match token account)
- Twitch Channel (starts with `#`)
- Perplexity API Key (starts with `pplx-`)

### Testing Tools
- `python setup_wizard.py` - Interactive setup
- `python test_credentials.py` - Validate credentials
- `python chatbot.py` - Run the bot
