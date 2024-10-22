import telebot
import gen  # Import the card generation module
import re

# Create your bot with the bot token
API_TOKEN = '6561482740:AAH4vIrIZCjTzy92MO2ux9OCbaTg7AMDpMs'
bot = telebot.TeleBot(API_TOKEN)

# Regex to validate and parse the user input for the /gen command
gen_pattern = re.compile(r'/gen (\d{6,})(?:\|(\d{2})\|(\d{2,4})\|(\d{3}))?')

# Function to handle the /gen command
@bot.message_handler(commands=['gen'])
def handle_gen(message):
    # Extract the command and validate it using regex
    match = gen_pattern.match(message.text)
    if match:
        # Extract the groups (BIN, month, year, CVC)
        bin_number, month, year, cvc = match.groups()

        # Truncate BIN to the first 6 digits for lookup
        truncated_bin = bin_number[:6]

        # Validate year length and adjust if necessary
        if year and len(year) == 2:
            year = f"20{year}"  # Convert to 4 digits

        # Generate the cards
        cards = gen.generate_cards(bin_number, month, year, cvc)

        # Get BIN details (using truncated BIN)
        bin_info = gen.get_bin_details(truncated_bin)

        # Format the output in monospace (with triple backticks for easy copying)
        cards_output = '𝙇𝙪𝙝𝙣 𝘼𝙣𝙙 𝙍𝙚𝙜𝙚𝙭 𝙑𝙚𝙧𝙞𝙛𝙞𝙚𝙙 ✅\n' + '\n'.join(cards) + '\n 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙚𝙙 25 𝙘𝙖𝙧𝙙𝙨 🔰 '
        
        # Show BIN details along with the generated cards in monospace
        bin_info_output = f"\nBIN Details:\nBank: {bin_info['Bank']}\nCountry: {bin_info['Country']}\nCard Type: {bin_info['Card Type']}"
        
        bot.reply_to(message, f"Generated 25 cards:\n{cards_output}{bin_info_output}")
    else:
        # If the format is wrong, send an error message
        bot.reply_to(message, "𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙤𝙧𝙢𝙖𝙩. 𝙐𝙨𝙚: /𝙜𝙚𝙣 𝘽𝙄𝙉|𝙈𝙈|𝙔𝙔𝙔𝙔|𝘾𝙑𝘾 𝙤𝙧 𝙨𝙞𝙢𝙥𝙡𝙮 /𝙜𝙚𝙣 𝘽𝙄𝙉")

# Start polling to listen for new messages
bot.polling()
