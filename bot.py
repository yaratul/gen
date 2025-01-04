import telebot
from core import check_card, load_proxies

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

# Start polling
print("Bot is running...")
bot.polling()
