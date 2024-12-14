import random
import telebot
from gen import generate_luhn_compliant_card
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Replace this with your actual Telegram bot token from BotFather
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'
bot = telebot.TeleBot(TOKEN)

# User session data for settings
user_sessions = {}

# Generate a valid card number using the Luhn algorithm
def generate_card(bin_prefix, month, year, cvv_length, fixed_cvv):
    card_number = generate_luhn_compliant_card(bin_prefix)
    expiration_month = month if month else f"{random.randint(1, 12):02d}"
    expiration_year = year if year else random.randint(2025, 2030)
    cvv = fixed_cvv if fixed_cvv else ''.join([str(random.randint(0, 9)) for _ in range(cvv_length)])
    return f"{card_number}|{expiration_month}|{expiration_year}|{cvv}"

# Start interaction with /gen
@bot.message_handler(commands=['gen'])
def start_gen(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {
        'bin': '47985100',  # Default BIN
        'quantity': 5,  # Default card quantity
        'cvv_length': 3,  # Default CVV length
        'month': None,  # Default: Random month
        'year': None,  # Default: Random year
        'fixed_cvv': None,  # Default: Random CVV
    }

    # Create an interactive keyboard
    keyboard = create_settings_keyboard(chat_id)
    bot.send_message(chat_id, "Customize your settings below:", reply_markup=keyboard)

# Create settings keyboard
def create_settings_keyboard(chat_id):
    user_data = user_sessions[chat_id]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(f"BIN: {user_data['bin']}", callback_data="edit_bin"),
        InlineKeyboardButton(f"Quantity: {user_data['quantity']}", callback_data="edit_quantity"),
    )
    keyboard.add(
        InlineKeyboardButton(f"Month: {user_data['month'] or 'Random'}", callback_data="edit_month"),
        InlineKeyboardButton(f"Year: {user_data['year'] or 'Random'}", callback_data="edit_year"),
    )
    keyboard.add(
        InlineKeyboardButton(f"CVV: {user_data['fixed_cvv'] or 'Random'}", callback_data="edit_cvv"),
        InlineKeyboardButton("✅ Generate Cards", callback_data="generate_cards"),
    )
    return keyboard

# Handle button interactions
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if chat_id not in user_sessions:
        bot.answer_callback_query(call.id, "Session expired. Please use /gen.")
        return

    if call.data == "edit_bin":
        msg = bot.send_message(chat_id, "Enter the BIN (minimum 6 digits):")
        bot.register_next_step_handler(msg, set_bin)

    elif call.data == "edit_quantity":
        msg = bot.send_message(chat_id, "Enter the quantity (1-50):")
        bot.register_next_step_handler(msg, set_quantity)

    elif call.data == "edit_month":
        msg = bot.send_message(chat_id, "Enter the expiration month (01-12) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_month)

    elif call.data == "edit_year":
        msg = bot.send_message(chat_id, "Enter the expiration year (2024-2035) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_year)

    elif call.data == "edit_cvv":
        msg = bot.send_message(chat_id, "Enter a fixed CVV (3-4 digits) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_cvv)

    elif call.data == "generate_cards":
        generate_cards(call)

# Set BIN
def set_bin(message):
    chat_id = message.chat.id
    bin_value = message.text.strip()
    if len(bin_value) >= 6 and bin_value.isdigit():
        user_sessions[chat_id]['bin'] = bin_value
        bot.send_message(chat_id, f"BIN updated to {bin_value}.", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "Invalid BIN. Please enter at least 6 digits.")

# Set quantity
def set_quantity(message):
    chat_id = message.chat.id
    try:
        quantity = int(message.text.strip())
        if 1 <= quantity <= 50:
            user_sessions[chat_id]['quantity'] = quantity
            bot.send_message(chat_id, f"Quantity updated to {quantity}.", reply_markup=create_settings_keyboard(chat_id))
        else:
            bot.send_message(chat_id, "Quantity must be between 1 and 50.")
    except ValueError:
        bot.send_message(chat_id, "Invalid quantity. Please enter a number between 1 and 50.")

# Set month
def set_month(message):
    chat_id = message.chat.id
    month = message.text.strip()
    if month.lower() == 'rnd':
        user_sessions[chat_id]['month'] = None
        bot.send_message(chat_id, "Month set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif month.isdigit() and 1 <= int(month) <= 12:
        user_sessions[chat_id]['month'] = f"{int(month):02d}"
        bot.send_message(chat_id, f"Month updated to {month}.", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "Invalid month. Please enter a number between 01 and 12 or 'rnd'.")

# Set year
def set_year(message):
    chat_id = message.chat.id
    year = message.text.strip()
    if year.lower() == 'rnd':
        user_sessions[chat_id]['year'] = None
        bot.send_message(chat_id, "Year set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif year.isdigit() and 2024 <= int(year) <= 2035:
        user_sessions[chat_id]['year'] = int(year)
        bot.send_message(chat_id, f"Year updated to {year}.", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "Invalid year. Please enter a number between 2024 and 2035 or 'rnd'.")

# Set CVV
def set_cvv(message):
    chat_id = message.chat.id
    cvv = message.text.strip()
    if cvv.lower() == 'rnd':
        user_sessions[chat_id]['fixed_cvv'] = None
        bot.send_message(chat_id, "CVV set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif cvv.isdigit() and len(cvv) in [3, 4]:
        user_sessions[chat_id]['fixed_cvv'] = cvv
        bot.send_message(chat_id, f"CVV updated to {cvv}.", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "Invalid CVV. Please enter 3-4 digits or 'rnd'.")

# Generate cards
def generate_cards(call):
    chat_id = call.message.chat.id
    user_data = user_sessions[chat_id]
    bin_prefix = user_data['bin']
    quantity = user_data['quantity']
    month = user_data['month']
    year = user_data['year']
    cvv_length = 3 if user_data['fixed_cvv'] is None else len(user_data['fixed_cvv'])
    fixed_cvv = user_data['fixed_cvv']

    cards = [generate_card(bin_prefix, month, year, cvv_length, fixed_cvv) for _ in range(quantity)]
    cards_output = "\n".join(cards)

    bot.send_message(chat_id, f"Generated Cards:\n\n{cards_output}")

# Start the bot
bot.polling(none_stop=True)
