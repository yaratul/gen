import random
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# User session data for settings
user_sessions = {}

# APIs
WAIFU_API = "https://api.waifu.pics/sfw/waifu"
BIN_LOOKUP_API = "https://lookup.binlist.net/"  # Free BIN lookup API

# Generate a valid card number using the Luhn algorithm
def generate_luhn_compliant_card(bin_prefix):
    num = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(15 - len(bin_prefix))])
    checksum = 0
    reversed_digits = map(int, reversed(num))
    for i, digit in enumerate(reversed_digits):
        if i % 2 == 0:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return num + str((10 - (checksum % 10)) % 10)

def generate_card(bin_prefix, month, year, cvv_length, fixed_cvv):
    card_number = generate_luhn_compliant_card(bin_prefix)
    exp_month = month or f"{random.randint(1, 12):02d}"
    exp_year = year or random.randint(2024, 2035)
    cvv = fixed_cvv or ''.join([str(random.randint(0, 9)) for _ in range(cvv_length)])
    return f"{card_number}|{exp_month}|{exp_year}|{cvv}"

def start_gen(bot, message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {
        'bin': None,
        'quantity': 5,
        'cvv_length': 3,
        'month': None,
        'year': None,
        'fixed_cvv': None,
    }

    # Fetch waifu image
    waifu_image = requests.get(WAIFU_API).json().get("url", None)

    # Create the interactive keyboard
    keyboard = create_settings_keyboard(chat_id)

    # Send message with waifu image
    if waifu_image:
        bot.send_photo(chat_id, waifu_image, caption="🛠 **Customize your settings below:**", reply_markup=keyboard, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "🛠 **Customize your settings below:**", reply_markup=keyboard, parse_mode="Markdown")

def create_settings_keyboard(chat_id):
    user_data = user_sessions[chat_id]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(f"BIN: {user_data['bin'] or 'Not Set'}", callback_data="gen_edit_bin"),
        InlineKeyboardButton(f"Quantity: {user_data['quantity']}", callback_data="gen_edit_quantity"),
    )
    keyboard.add(
        InlineKeyboardButton(f"Month: {user_data['month'] or 'Random'}", callback_data="gen_edit_month"),
        InlineKeyboardButton(f"Year: {user_data['year'] or 'Random'}", callback_data="gen_edit_year"),
    )
    keyboard.add(
        InlineKeyboardButton(f"CVV: {user_data['fixed_cvv'] or 'Random'}", callback_data="gen_edit_cvv"),
        InlineKeyboardButton("✅ Generate Cards", callback_data="gen_generate_cards"),
    )
    return keyboard

def get_bin_details(bin_prefix):
    try:
        response = requests.get(BIN_LOOKUP_API + bin_prefix)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def format_bin_details(bin_data):
    if bin_data:
        brand = bin_data.get("scheme", "Unknown").upper()
        bin_type = bin_data.get("type", "Unknown").upper()
        level = bin_data.get("brand", "Unknown")
        issuer = bin_data.get("bank", {}).get("name", "Unknown")
        country = bin_data.get("country", {}).get("name", "Unknown")
        emoji = bin_data.get("country", {}).get("emoji", "")
        return f"""
𝗕𝗜𝗡 ⇾ `{bin_data.get("number", {}).get("prefix", 'Unknown')}`
𝗕𝗿𝗮𝗻𝗱 ⇾ {brand}
𝗧𝘆𝗽𝗲 ⇾ {bin_type}
𝗟𝗲𝘃𝗲𝗹 ⇾ {level}
𝗜𝘀𝘀𝘂𝗲𝗿 ⇾ {issuer}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country} {emoji}
        """
    else:
        return "❌ **BIN details not found**"

def handle_callbacks(bot, call):
    chat_id = call.message.chat.id
    if chat_id not in user_sessions:
        bot.answer_callback_query(call.id, "Session expired. Please use /start.")
        return

    if call.data == "gen_edit_bin":
        msg = bot.send_message(chat_id, "Enter the BIN (minimum 6 digits):")
        bot.register_next_step_handler(msg, set_bin, bot)

    elif call.data == "gen_edit_quantity":
        msg = bot.send_message(chat_id, "Enter the quantity (1-50):")
        bot.register_next_step_handler(msg, set_quantity, bot)

    elif call.data == "gen_edit_month":
        msg = bot.send_message(chat_id, "Enter the expiration month (01-12) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_month, bot)

    elif call.data == "gen_edit_year":
        msg = bot.send_message(chat_id, "Enter the expiration year (2024-2035) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_year, bot)

    elif call.data == "gen_edit_cvv":
        msg = bot.send_message(chat_id, "Enter a fixed CVV (3-4 digits) or type 'rnd' for random:")
        bot.register_next_step_handler(msg, set_cvv, bot)

    elif call.data == "gen_generate_cards":
        generate_cards(bot, chat_id)

# Define handlers for updating user session
def set_bin(message, bot):
    chat_id = message.chat.id
    bin_value = message.text.strip()
    if len(bin_value) >= 6 and bin_value.isdigit():
        user_sessions[chat_id]['bin'] = bin_value
        bot.send_message(chat_id, f"BIN updated to `{bin_value}`.", parse_mode="Markdown", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "❌ Invalid BIN. Please enter at least 6 digits.")

def set_quantity(message, bot):
    chat_id = message.chat.id
    try:
        quantity = int(message.text.strip())
        if 1 <= quantity <= 50:
            user_sessions[chat_id]['quantity'] = quantity
            bot.send_message(chat_id, f"Quantity updated to `{quantity}`.", parse_mode="Markdown", reply_markup=create_settings_keyboard(chat_id))
        else:
            bot.send_message(chat_id, "❌ Enter a valid quantity between 1 and 50.")
    except ValueError:
        bot.send_message(chat_id, "❌ Please enter a valid number.")

def set_month(message, bot):
    chat_id = message.chat.id
    month = message.text.strip()
    if month.lower() == "rnd":
        user_sessions[chat_id]['month'] = None
        bot.send_message(chat_id, "Expiration month set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif month.isdigit() and 1 <= int(month) <= 12:
        user_sessions[chat_id]['month'] = f"{int(month):02d}"
        bot.send_message(chat_id, f"Month updated to `{user_sessions[chat_id]['month']}`.", parse_mode="Markdown", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "❌ Invalid month. Enter a value between 01 and 12, or type 'rnd'.")

def set_year(message, bot):
    chat_id = message.chat.id
    year = message.text.strip()
    if year.lower() == "rnd":
        user_sessions[chat_id]['year'] = None
        bot.send_message(chat_id, "Expiration year set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif year.isdigit() and 2024 <= int(year) <= 2035:
        user_sessions[chat_id]['year'] = int(year)
        bot.send_message(chat_id, f"Year updated to `{year}`.", parse_mode="Markdown", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "❌ Invalid year. Enter a value between 2024 and 2035, or type 'rnd'.")

def set_cvv(message, bot):
    chat_id = message.chat.id
    cvv = message.text.strip()
    if cvv.lower() == "rnd":
        user_sessions[chat_id]['fixed_cvv'] = None
        bot.send_message(chat_id, "CVV set to random.", reply_markup=create_settings_keyboard(chat_id))
    elif cvv.isdigit() and 3 <= len(cvv) <= 4:
        user_sessions[chat_id]['fixed_cvv'] = cvv
        bot.send_message(chat_id, f"CVV updated to `{cvv}`.", parse_mode="Markdown", reply_markup=create_settings_keyboard(chat_id))
    else:
        bot.send_message(chat_id, "❌ Invalid CVV. Enter a value with 3-4 digits, or type 'rnd'.")

def generate_cards(bot, chat_id):
    user_data = user_sessions[chat_id]
    bin_prefix = user_data['bin']
    if not bin_prefix:
        bot.send_message(chat_id, "❌ **Please set a BIN first!**")
        return

    cards = [
        generate_card(
            bin_prefix,
            user_data['month'],
            user_data['year'],
            user_data['cvv_length'],
            user_data['fixed_cvv']
        )
        for _ in range(user_data['quantity'])
    ]
    cards_output = "\n".join(cards)

    bin_data = get_bin_details(bin_prefix)
    bin_details = format_bin_details(bin_data)

    # Fetch waifu image
    waifu_image = requests.get(WAIFU_API).json().get("url", None)

    if waifu_image:
        bot.send_photo(chat_id, waifu_image, caption=f"{bin_details}\n\n🔥 **Here are your generated CC's:** 🔥\n\n`{cards_output}`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, f"{bin_details}\n\n🔥 **Here are your generated CC's:** 🔥\n\n`{cards_output}`", parse_mode="Markdown")
