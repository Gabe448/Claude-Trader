import nextcord
from nextcord.ext import commands
import anthropic
import os
import base64
import io
from datetime import datetime

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

@bot.command(name='trade')
async def analyze_trade(ctx, *, user_message: str = "Analyze this chart"):
    """
    Analyze a trading chart using Claude
    Usage: !claude trade [optional context]
    Attach a chart image to your message
    """
    # Check if image is attached
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a chart image to analyze!")
        return
    
    # Send thinking message
    thinking_msg = await ctx.send("🤔 Analyzing chart...")
    
    try:
        # Get the first attachment (image)
        attachment = ctx.message.attachments[0]
        
        # Check if it's an image
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            await thinking_msg.edit(content="❌ Please attach an image file (PNG, JPG, etc.)")
            return
        
        # Download image
        image_data = await attachment.read()
        
        # Convert to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine media type
        media_type = attachment.content_type
        
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
                            "text": f"{user_message}\n\nProvide a complete trading analysis following the confluence framework. Include: patterns, key levels, volume, directional bias, and specific trade setup if 3+ signals present."
                        }
                    ]
                }
            ]
        )
        
        # Extract response
        response_text = message.content[0].text
        
        # Split response if too long (Discord limit is 2000 chars)
        if len(response_text) <= 2000:
            await thinking_msg.edit(content=f"📊 **Trading Analysis**\n\n{response_text}")
        else:
            # Split into multiple messages
            chunks = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
            await thinking_msg.edit(content=f"📊 **Trading Analysis** (Part 1/{len(chunks)})\n\n{chunks[0]}")
            
            for i, chunk in enumerate(chunks[1:], 2):
                await ctx.send(f"📊 **Trading Analysis** (Part {i}/{len(chunks)})\n\n{chunk}")
        
    except anthropic.APIError as e:
        await thinking_msg.edit(content=f"❌ API Error: {str(e)}")
    except Exception as e:
        await thinking_msg.edit(content=f"❌ Error: {str(e)}")

@bot.command(name='help')
async def help_command(ctx):
    """Show bot commands"""
    help_text = """
📈 **Trading Bot Commands**

`!trade [optional context]` - Analyze a chart
  • Attach a chart image
  • Optionally add context like "focus on volume" or "looking at 4h timeframe"
  • Bot will analyze using confluence trading strategy

**Example:**
```
!trade What do you see here?
```
(with chart image attached)

**Strategy:** Confluence-based technical analysis requiring 3+ confirming signals before any trade recommendation.
    """
    await ctx.send(help_text)

# Run bot
if __name__ == '__main__':
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set!")
    else:
        bot.run(token)
