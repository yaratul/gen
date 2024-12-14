import telebot
import gen  # Import the enhanced gen.py script
import re
import os

# Your Telegram Bot API token
API_TOKEN = '6561482740:AAG0oFldylLCXz5lvPaantgKMntdBZv5Fxw'
bot = telebot.TeleBot(API_TOKEN)

# Regex to validate and parse the user input for the /gen command
gen_pattern = re.compile(r'/gen (\d{6,})(?:\s+(\d+))?')

# Function to handle the /gen command
@bot.message_handler(commands=['gen'])
def handle_gen(message):
    """
    Handle the /gen command to generate cards based on user input.
    """
    match = gen_pattern.match(message.text)
    if not match:
        bot.reply_to(message, "❌ Invalid format. Use: `/gen BIN QUANTITY`\n"
                              "Example: `/gen 434257 100`", parse_mode='Markdown')
        return

    bin_number, quantity = match.groups()

    try:
        # Parse quantity or default to 25
        quantity = int(quantity) if quantity else 25
        if len(bin_number) < 6 or not bin_number.isdigit():
            raise ValueError("BIN must be a valid 6-digit number.")
        if quantity < 1 or quantity > 5000:
            raise ValueError("Quantity must be between 1 and 5000.")

        # Generate the cards
        cards = gen.generate_cards(bin_number, quantity)

        if quantity <= 25:
            # Reply directly with card details for small quantities
            cards_output = "\n".join(cards)
            bin_info = gen.get_bin_details(bin_number)
            bin_info_message = (
                f"✅ Generated {quantity} cards:\n\n"
                f"{cards_output}\n\n"
                f"🔰 BIN Details:\n"
                f"Bank: {bin_info['Bank']}\n"
                f"Country: {bin_info['Country']}\n"
                f"Card Type: {bin_info['Card Type']}"
            )
            bot.reply_to(message, bin_info_message)
        else:
            # Save the generated cards to a temporary file
            file_path = f"generated_cards_{bin_number}.txt"
            try:
                with open(file_path, "w") as file:
                    file.write("\n".join(cards))

                # Send the file
                with open(file_path, "rb") as file:
                    bot.send_document(message.chat.id, file)

                # Delete the file after sending
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                bot.reply_to(message, f"❌ Error handling file: {e}")
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Send BIN details separately
            bin_info = gen.get_bin_details(bin_number)
            bin_info_message = (
                f"✅ Cards generated successfully!\n\n"
                f"🔰 BIN Details:\n"
                f"Bank: {bin_info['Bank']}\n"
                f"Country: {bin_info['Country']}\n"
                f"Card Type: {bin_info['Card Type']}\n\n"
                f"📄 Total cards generated: {quantity}."
            )
            bot.reply_to(message, bin_info_message, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# Function to handle invalid commands
@bot.message_handler(func=lambda message: True)
def invalid_command(message):
    """
    Catch-all handler for invalid commands.
    """
    bot.reply_to(message, "❌ Unrecognized command. Use `/gen BIN QUANTITY`.")

# Start polling to listen for new messages
bot.polling()
