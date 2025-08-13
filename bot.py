import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
FOREX_API_KEY = os.environ.get("FOREX_API_KEY")  # Your Twelve Data API key

# SL and TP in pips (adjust as needed)
SL_PIPS = 10
TP_PIPS = 20

# Strategy: simple price vs placeholder moving average
def strategy(price, moving_average):
    if price > moving_average:
        return "UP"
    else:
        return "DOWN"

# Convert pips to price adjustment
def calculate_sl_tp(price, direction):
    pip_value = 0.0001  # Standard for most Forex pairs
    if direction == "UP":
        sl = price - SL_PIPS * pip_value
        tp = price + TP_PIPS * pip_value
    else:  # DOWN
        sl = price + SL_PIPS * pip_value
        tp = price - TP_PIPS * pip_value
    return round(sl, 5), round(tp, 5)

# /signal command
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or "/" not in context.args[0]:
        await update.message.reply_text("Usage: /signal EUR/USD")
        return

    base, target = context.args[0].upper().split("/")

    try:
        # Fetch price from Twelve Data
        response = requests.get(
            "https://api.twelvedata.com/price",
            params={
                "symbol": f"{base}/{target}",
                "apikey": FOREX_API_KEY
            }
        )
        data = response.json()
        if "price" in data:
            price = float(data["price"])
            
            # Placeholder moving average - for now just using price
            moving_average = price
            direction = strategy(price, moving_average)
            sl, tp = calculate_sl_tp(price, direction)
            
            message = (
                f"💱 {base}/{target}\n"
                f"Signal: {direction}\n"
                f"Price: {price}\n"
                f"Stop Loss: {sl}\n"
                f"Take Profit: {tp}"
            )
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Could not fetch rate right now.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Forex Signal Bot Online ✅\n"
        "Use /signal [PAIR] to get your signal.\n"
        "Example: /signal EUR/USD"
    )

# Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.run_polling()

if __name__ == "__main__":
    main()
