import telebot
from skk import fetch_stripe_details
from gen import generate_cards


# Initialize the bot with your token
BOT_TOKEN = "6561482740:AAEVvL8AOkskJ91wlGV8MM5qAbi5OZmagSY"
bot = telebot.TeleBot(BOT_TOKEN)

# Command handler for Stripe Key Retrieval
@bot.message_handler(commands=["sk"])
@bot.message_handler(func=lambda message: message.text.startswith(".sk"))
def handle_skk_command(message):
    try:
        # Extract the Stripe key from the command
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(
                message,
                "Usage: /skk <Stripe Secret Key>\nExample: /skk sk_live_12345",
            )
            return

        stripe_key = parts[1]
        response = bot.reply_to(message, "Fetching details, please wait...")

        # Fetch details using skk.py
        results = fetch_stripe_details(stripe_key)

        if isinstance(results, str):
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=response.message_id,
                text=f"Error: {results}",
            )
        else:
            output = "𝗦𝘁𝗿𝗶𝗽𝗲 𝗞𝗲𝘆 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:\n\n"
            for section, info in results.items():
                output += f"{section.upper()}:\n"
                if isinstance(info, dict):
                    for key, value in info.items():
                        output += f"- {key}: {value}\n"
                elif isinstance(info, list):
                    for i, item in enumerate(info, start=1):
                        output += f"{i}:\n"
                        for subkey, subvalue in item.items():
                            output += f"  {subkey}: {subvalue}\n"
                output += "\n"

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=response.message_id,
                text=output,
                parse_mode="Markdown",
            )
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Command handler for /gen and .gen
@bot.message_handler(commands=["gen"])
@bot.message_handler(func=lambda message: message.text.startswith(".gen"))
def handle_gen_command(message):
    try:
        # Extract BIN and amount from the message
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(
                message,
                "Usage: /gen <BIN>[|MM|YY|CVV] [amount]\nExample: /gen 404609 25\nExample with constants: /gen 519959302061|10|27|517 10",
            )
            return

        bin_input = parts[1]
        amount = int(parts[2]) if len(parts) > 2 else 25  # Default to 25 cards if amount not provided

        # Generate cards
        response = bot.reply_to(message, "Generating cards, please wait...")
        cards, bin_info = generate_cards(bin_input, amount)

        # Format the output in monospace for Telegram
        card_output = "\n".join([f"`{card}`" for card in cards])
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=response.message_id,
            text=(
                f"𝗕𝗜𝗡 ⇾ `{bin_input}`\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ `{amount}`\n\n{card_output}\n\n𝗜𝗻𝗳𝗼:\n`{bin_info}`"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Run the bot
bot.polling()
