import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
FOREX_API_KEY = os.environ.get("FOREX_API_KEY")  # Put your Forex API key in Railway

# Parameters for SL and TP (adjustable)
SL_PIPS = 10
TP_PIPS = 20

# Example Forex API endpoint template (replace with your provider's actual URL)
FOREX_BASE_URL = "https://api.yourforexprovider.com/latest"

# Strategy: simple price vs moving average (placeholder, you can improve later)
def strategy(price, moving_average):
    if price > moving_average:
        return "UP"
    else:
        return "DOWN"

# Convert pips to price adjustment (example for USD pairs)
def calculate_sl_tp(price, direction):
    pip_value = 0.0001  # For most currency pairs
    if direction == "UP":
        sl = price - SL_PIPS * pip_value
        tp = price + TP_PIPS * pip_value
    else:  # DOWN
        sl = price + SL_PIPS * pip_value
        tp = price - TP_PIPS * pip_value
    return round(sl, 5), round(tp, 5)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or "/" not in context.args[0]:
        await update.message.reply_text("Usage: /signal EUR/USD")
        return

    base, target = context.args[0].upper().split("/")

    try:
        # Make request to your Forex API
        response = requests.get(
            FOREX_BASE_URL,
            params={
                "apikey": FOREX_API_KEY,
                "base": base,
                "symbols": target
            }
        )
        data = response.json()
        
        if "rates" in data and target in data["rates"]:
            price = data["rates"][target]
            
            # Placeholder moving average - you can replace with last N prices from API
            moving_average = price  # For simplicity, currently using price itself
            direction = strategy(price, moving_average)
            sl, tp = calculate_sl_tp(price, direction)
            
            message = f"💱 {base}/{target}\nSignal: {direction}\nPrice: {price}\nStop Loss: {sl}\nTake Profit: {tp}"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Could not fetch rate right now.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Forex Signal Bot Online ✅\nUse /signal [PAIR] to get your signal.\nExample: /signal EUR/USD"
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.run_polling()

if __name__ == "__main__":
    main()
