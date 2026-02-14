import nextcord
from nextcord.ext import commands
import anthropic
import os
import base64
import io
from datetime import datetime
from PIL import Image

# Bot setup
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# API clients
claude_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Trading strategy system prompt
TRADING_STRATEGY = """You are an expert trading analyst using a comprehensive confluence-based trading strategy.

CORE PHILOSOPHY:
- Confluence Trading: Require 3+ confirming signals before any trade
- Trigger-Based Execution: Define clear entry/exit levels
- Capital Preservation > Being Right: Missing trades costs nothing

KEY PATTERNS YOU KNOW:
- Reversal: Head & Shoulders, Double Top/Bottom, Falling/Rising Wedges
- Continuation: Cup & Handle, Triangles (Ascending/Descending/Symmetrical)

INDICATORS YOU USE:
- EMAs (20, 50, 100, 200): Check stack, direction, price location
- VWAP: Intraday only, reclaims/breaks are significant
- Volume: Must be 1.5x+ average to confirm moves
- Bollinger Bands & Keltner: Squeeze = breakout imminent

CRITICAL RULES:
1. Multiple Resistance Rejections (3+) = Reversal likely
2. Long Wicks at Extremes = Rejection/Reversal points
3. EMA Reclaim/Loss = Trend confirmation
4. Volume Spike at Lows = Capitulation (bullish)
5. Failed Breakouts → Opposite direction move
6. Don't fight 200 EMA without strong reason

CONFLUENCE CHECKLIST (need 3+):
✓ Pattern (wedge, triangle, H&S, etc.)
✓ Level (support/resistance, EMA, prior swing)
✓ Rejection (wick, failed breakout)
✓ Volume (1.5x+ surge)
✓ Trend alignment (with 200 EMA)

ANALYSIS FORMAT:
1. Pattern Recognition: What patterns do you see?
2. Key Levels: Support/resistance, EMAs
3. Volume Analysis: Normal, surging, declining?
4. Confluence Signals: Count confirming signals
5. Directional Bias: BULLISH/BEARISH/WAIT (with conviction level)
6. Trade Setup (if 3+ signals):
   - Entry trigger
   - Targets (multiple levels)
   - Stop loss
   - Risk/reward ratio

MISTAKES TO AVOID:
- Don't call trades on single indicators
- Check if EMAs rising/falling (not just position)
- No wick on breakdown = continuation, not reversal
- 3+ rejections at level = distribution, not consolidation
- Parabolic moves = exhaustion, wait for reset

Be direct, confident when you have 3+ signals, and say WAIT when you don't."""

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.slash_command(name='trade', description='Analyze a trading chart using AI')
async def analyze_trade(
    interaction: nextcord.Interaction,
    image: nextcord.Attachment = nextcord.SlashOption(description="Chart image to analyze", required=True),
    context: str = nextcord.SlashOption(description="Optional analysis context (e.g., 'focus on volume')", required=False, default="Analyze this chart")
):
    """
    Analyze a trading chart using Claude
    """
    # Defer the response (ephemeral = only you can see it)
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Check if it's an image
        if not image.content_type or not image.content_type.startswith('image/'):
            await interaction.followup.send("❌ Please attach an image file (PNG, JPG, etc.)", ephemeral=True)
            return
        
        # Download image
        image_data = await image.read()
        
        # Convert image to PNG format (works best with Claude)
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as PNG to bytes
        png_buffer = io.BytesIO()
        img.save(png_buffer, format='PNG')
        png_bytes = png_buffer.getvalue()
        
        # Convert to base64
        base64_image = base64.b64encode(png_bytes).decode('utf-8')
        media_type = 'image/png'
        
        # Call Claude API
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=TRADING_STRATEGY,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": f"{context}\n\nProvide a complete trading analysis following the confluence framework. Include: patterns, key levels, volume, directional bias, and specific trade setup if 3+ signals present."
                        }
                    ]
                }
            ]
        )
        
        # Extract response
        response_text = message.content[0].text
        
        # Send response (ephemeral - only visible to user)
        if len(response_text) <= 2000:
            await interaction.followup.send(f"📊 **Trading Analysis:**\n\n{response_text}", ephemeral=True)
        else:
            # Split into multiple messages
            chunks = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
            await interaction.followup.send(f"📊 **Trading Analysis** (Part 1/{len(chunks)}):\n\n{chunks[0]}", ephemeral=True)
            
            for i, chunk in enumerate(chunks[1:], 2):
                await interaction.followup.send(f"📊 **Trading Analysis** (Part {i}/{len(chunks)}):\n\n{chunk}", ephemeral=True)
        
    except anthropic.APIError as e:
        await interaction.followup.send(f"❌ API Error: {str(e)}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

@bot.slash_command(name='tradehelp', description='Show trading bot commands and info')
async def help_command(interaction: nextcord.Interaction):
    """Show bot commands"""
    help_text = """
📈 **Trading Bot Commands**

`/trade` - Analyze a chart
  • Upload a chart image
  • Optionally add context like "focus on volume" or "looking at 4h timeframe"
  • Bot will analyze using confluence trading strategy
  • **Response is private - only you can see it!**

**Strategy:** Confluence-based technical analysis requiring 3+ confirming signals before any trade recommendation.
    """
    await interaction.response.send_message(help_text, ephemeral=True)

# Run bot
if __name__ == '__main__':
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set!")
    else:
        bot.run(token)
