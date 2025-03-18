import telebot
import re
import os
from gen1 import generate_cards, fetch_bin_info
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the bot with your token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Webshare.io proxy configuration
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_PROTOCOL = os.getenv("PROXY_PROTOCOL")

PROXY_URL = f"{PROXY_PROTOCOL}://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# Command handler for /gen (card generation)
@bot.message_handler(commands=['gen'])
@bot.message_handler(func=lambda message: message.text.startswith(".gen"))
def gen_command(message):
    try:
        # Extract the input
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            bot.reply_to(message, "Usage: /gen <BIN or card format> [amount (up to 3000)]")
            return

        bin_input = args[1].strip()
        amount = int(args[2]) if len(args) > 2 and args[2].isdigit() else 10

        # Validate the amount
        if amount > 3000:
            bot.reply_to(message, "Error: Amount cannot exceed 3000 cards.")
            return
        elif amount < 1:
            bot.reply_to(message, "Error: Amount must be at least 1 card.")
            return

        # Parse the input to detect constant month, year, and CVV
        match = re.match(r"(\d+)(?:\|(\d{2}))?(?:\|(\d{4}|\d{2}|xxxx))?(?:\|(\d+|xxx))?", bin_input)
        if not match:
            bot.reply_to(message, "Error: Invalid BIN format.")
            return

        card_bin = match.group(1)
        constant_month = match.group(2) if match.group(2) else None
        constant_year = match.group(3) if match.group(3) != "xxxx" else None
        constant_cvv = match.group(4) if match.group(4) != "xxx" else None

        # Generate cards
        cards, bin_info = generate_cards(
            bin_input=card_bin,
            amount=amount,
            constant_month=int(constant_month) if constant_month else None,
            constant_year=int(constant_year) if constant_year else None,
            constant_cvv=constant_cvv
        )

        if isinstance(cards, str):  # If an error occurs, return the message
            bot.reply_to(message, cards)
            return

        # Prepare the response
        bin_prefix = card_bin[:6] if len(card_bin) >= 6 else "Unknown"
        if amount > 10:
            # Save the cards to a temporary file
            file_path = f"generated_cards_{bin_prefix}.txt"
            with open(file_path, 'w') as f:
                f.write("\n".join(cards))

            # Send the file
            with open(file_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption=f"𝗕𝗜𝗡 ⇾ {bin_prefix}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {amount}\n\n𝗜𝗻𝗳𝗼: {bin_info}")

            # Delete the file immediately after sending
            os.remove(file_path)
        else:
            # Prepare inline text response for small amounts
            response = f"𝗕𝗜𝗡 ⇾ {bin_prefix}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {len(cards)}\n\n"
            response += "\n".join(cards)
            response += f"\n\n𝗜𝗻𝗳𝗼: {bin_info}"
            bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /gen <BIN or card format> [amount (up to 3000)]")

# Flask app for Render
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Bot is running!'

# Start the Flask app
if __name__ == '__main__':
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url=f"https://gen-kkw5.onrender.com/{BOT_TOKEN}")

    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
