import telebot
import re
import os
from gen1 import generate_cards, fetch_bin_info
from core import check_card  # Import the check_card function from core.py
from flask import Flask, request
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Initialize the bot with your token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# MongoDB connection for caching BIN details
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["bin_database"]
collection = db["bin_details"]

# Command handler for /chk (single card check)
@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda message: message.text.startswith(".chk"))
def chk_command(message):
    try:
        # Extract the input
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Usage: /chk <card_number|exp_month|exp_year|cvc> or .chk <card_number|exp_month|exp_year|cvc>")
            return

        # Parse the input
        card_input = args[1].strip()
        card_parts = card_input.split("|")
        if len(card_parts) != 4:
            bot.reply_to(message, "Error: Invalid format. Use <card_number|exp_month|exp_year|cvc>")
            return

        card_number, exp_month, exp_year, cvc = card_parts

        # Validate the card number
        if not card_number.isdigit() or len(card_number) < 15 or len(card_number) > 16:
            bot.reply_to(message, "Error: Invalid card number.")
            return

        # Validate expiration month and year
        if not exp_month.isdigit() or not exp_year.isdigit():
            bot.reply_to(message, "Error: Expiration month and year must be numbers.")
            return

        # Validate CVC
        if not cvc.isdigit() or len(cvc) < 3 or len(cvc) > 4:
            bot.reply_to(message, "Error: Invalid CVC.")
            return

        # Perform card check using core.py
        response = check_card(card_number, exp_month, exp_year, cvc)

        # Send the response to the user
        bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /chk <card_number|exp_month|exp_year|cvc> or .chk <card_number|exp_month|exp_year|cvc>")

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
