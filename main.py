import telebot
from gen import generate_cards

# Initialize the bot with your token
BOT_TOKEN = "6561482740:AAEVvL8AOkskJ91wlGV8MM5qAbi5OZmagSY"
bot = telebot.TeleBot(BOT_TOKEN)

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
