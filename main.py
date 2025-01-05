import telebot
from core import check_card, load_proxies
from gen1 import generate_cards  # Import the card generation tool from gen1.py
import os

# Initialize the bot with your token
BOT_TOKEN = "6561482740:AAF8rmN9I4mpAOm_BVfekqgv9raRprnUtlw"
bot = telebot.TeleBot(BOT_TOKEN)

# Load proxies
proxies = load_proxies('proxies.txt')

@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda message: message.text.startswith(".chk"))  
def handle_chk(message):


    try:
        # Extract the command argument
        args = message.text.split()
        if len(args) < 2:
            raise ValueError("Usage: /chk card_number|mm|yyyy|cvc")

        card_details = args[1]
        card_number, exp_month, exp_year, cvc = card_details.split('|')

        # Call the core.py function
        result = check_card(card_number, exp_month, exp_year, cvc, proxies)

        # Send the API's final response as-is
        bot.reply_to(message, result)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /chk card_number|mm|yyyy|cvc")

@bot.message_handler(commands=['gen'])
@bot.message_handler(func=lambda message: message.text.startswith(".gen"))  
def handle_gen(message):
    try:
        # Extract the command argument
        args = message.text.split()
        if len(args) < 2:
            raise ValueError("Usage: /gen BIN|mm|yy|cvv quantity")

        bin_input = args[1]
        quantity = int(args[2]) if len(args) > 2 else 25  # Default to 25 if no quantity is provided

        if quantity > 3000:
            raise ValueError("Maximum number of cards is 3000.")

        # Generate cards using the gen.py functionality and pass proxies
        cards, bin_info = generate_cards(bin_input, quantity, proxies)

        # Format the result for BIN info
        card_list = "\n".join(cards)

        # Save the generated cards to a .txt file
        file_name = f"generated_cards_{bin_input.replace('|', '')}.txt"
        with open(file_name, 'w') as f:
            f.write(f"BIN Info:\n{bin_info}\n\nGenerated Cards:\n{card_list}")

        # Send the file to the user
        with open(file_name, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"Here are your {quantity} generated cards!")

        # Clean up the file after sending
        os.remove(file_name)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /gen BIN|mm|yy|cvv quantity")

# Start polling
print("Bot is running...")
bot.polling()
