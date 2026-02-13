# Discord Trading Bot with Claude AI

A Discord bot that analyzes trading charts using Claude AI and your comprehensive confluence-based trading strategy.

## Features

- 📊 Analyzes chart images using Claude's vision
- 🎯 Uses your proven confluence trading strategy
- 🤖 Responds to `!trade` commands in Discord
- 📈 Provides detailed technical analysis with entry/exit levels

## Setup Instructions

### 1. Get API Keys

**Anthropic API Key:**
1. Go to https://console.anthropic.com
2. Sign up/login
3. Go to "API Keys" → "Create Key"
4. Copy the key

**Discord Bot Token:**
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Trading Bot")
4. Go to "Bot" tab → "Add Bot"
5. Under "TOKEN", click "Reset Token" → Copy it
6. Enable these **Privileged Gateway Intents**:
   - ✅ MESSAGE CONTENT INTENT
7. Go to "OAuth2" → "URL Generator"
8. Select scopes: `bot`
9. Select permissions: `Send Messages`, `Read Messages/View Channels`, `Attach Files`
10. Copy the generated URL and open it to invite bot to your server

### 2. Deploy to Railway

1. Create a new GitHub repository
2. Upload these files:
   - `bot.py`
   - `requirements.txt`
   - `nixpacks.toml`
   - `README.md`

3. Go to https://railway.app
4. "New Project" → "Deploy from GitHub repo"
5. Select your repository

6. Add environment variables:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key
   
   - Name: `DISCORD_BOT_TOKEN`
   - Value: Your Discord bot token

7. Deploy!

### 3. Use the Bot

In your Discord server:

```
!trade
```
(attach a chart image)

Or with context:
```
!trade Focus on the volume profile
```
(attach chart)

The bot will analyze using your confluence strategy and provide:
- Pattern recognition
- Key levels (support/resistance, EMAs)
- Volume analysis
- Confluence signal count
- Directional bias (BULLISH/BEARISH/WAIT)
- Specific trade setup if 3+ signals present

## Commands

- `!trade [context]` - Analyze attached chart
- `!help` - Show bot commands

## Strategy Summary

The bot uses your comprehensive confluence-based trading strategy requiring:
- **3+ confirming signals** before any trade
- Pattern + Level + Rejection/Volume + Trend alignment
- Clear entry/exit levels with risk/reward minimum 1:2
- Respects 200 EMA as trend filter
- Recognizes all major patterns (H&S, wedges, triangles, cup & handle)

## Costs

- **Anthropic API**: ~$0.03 per image analysis (Sonnet 4.5)
- **Railway**: Free tier available, then ~$5/month
- **Discord**: Free

## Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify both API keys are set correctly
- Ensure MESSAGE CONTENT INTENT is enabled

**"API Error":**
- Check your Anthropic account has credits
- Verify API key is correct

**Bot not in server:**
- Re-invite using OAuth2 URL with correct permissions
