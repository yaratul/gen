import telebot
import re
from cmd import handle_chk, handle_mchk
from gen1 import generate_cards, fetch_bin_info

# Initialize the bot with your token
BOT_TOKEN = "6561482740:AAF8rmN9I4mpAOm_BVfekqgv9raRprnUtlw"  # Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Load proxies
proxies = []
try:
    with open('proxies.txt', 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Proxies file not found. Ensure 'proxies.txt' exists.")

# Command handler for /chk (single card check)
@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda message: message.text.startswith(".chk"))
def chk_command(message):
    handle_chk(bot, message)

# Command handler for /mchk (mass card check)
@bot.message_handler(commands=['mchk'])
@bot.message_handler(func=lambda message: message.text.startswith(".mchk"))
def mchk_command(message):
    handle_mchk(bot, message)

# Command handler for /gen (card generation)
import os

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
            proxies=proxies,
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
  
# Start polling
print("Bot is running...")
bot.polling()
