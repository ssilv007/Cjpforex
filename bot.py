import os
import requests
import telebot
from time import sleep
import threading

# Telegram bot setup
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Channel or chat ID

# Forex API setup
FOREX_API_URL = "https://api.exchangerate.host/latest?base=USD&symbols=EUR,GBP,JPY"

# Function to fetch forex rates safely
def get_forex_rates():
    try:
        response = requests.get(FOREX_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
        return {}

# Command: /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Forex bot is online ✅")

# Command: /rates
@bot.message_handler(commands=['rates'])
def rates(message):
    rates = get_forex_rates()
    if rates:
        reply = "💱 Current Forex Rates 💱\n" + "\n".join([f"{k}: {v}" for k, v in rates.items()])
    else:
        reply = "❌ Could not fetch rates right now."
    bot.reply_to(message, reply)

# Automatic forex updates
def auto_post(interval=60):
    while True:
        rates = get_forex_rates()
        if rates:
            msg = "💱 Forex Rates Update 💱\n" + "\n".join([f"{k}: {v}" for k, v in rates.items()])
            try:
                bot.send_message(CHANNEL_ID, msg)
            except Exception as e:
                print(f"Error sending message: {e}")
        sleep(interval)

if __name__ == "__main__":
    # Start auto-posting in a background thread
    threading.Thread(target=auto_post, daemon=True).start()
    # Start Telegram polling
    bot.polling(none_stop=True)
