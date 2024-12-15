import random
import requests
import telebot
from gen import generate_luhn_compliant_card
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Replace this with your actual Telegram bot token
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'
bot = telebot.TeleBot(TOKEN)

# User session data for settings
user_sessions = {}


# Fetch BIN details from a free API
    # Fetch BIN details from multiple APIs
def fetch_bin_details(bin_prefix):
        try:
            # Primary API (BinList)
            response = requests.get(f"https://lookup.binlist.net/{bin_prefix}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "brand": data.get("scheme", "Unknown").upper(),
                    "type": data.get("type", "Unknown").upper(),
                    "level": data.get("brand", "Unknown").upper(),
                    "bank": data.get("bank", {}).get("name", "Unknown"),
                    "country": data.get("country", {}).get("name", "Unknown"),
                    "emoji": data.get("country", {}).get("emoji", ""),
                }
            elif response.status_code == 404:
                return {"brand": "Unknown", "type": "Unknown", "level": "Unknown", "bank": "Unknown", "country": "Unknown", "emoji": ""}
        except Exception as e:
            print(f"Error with BinList API: {e}")

        # Fallback API (another free BIN lookup service)
        try:
            fallback_response = requests.get(f"https://api.bincodes.com/bin/?format=json&api_key=YOUR_API_KEY&bin={bin_prefix}", timeout=5)
            if fallback_response.status_code == 200:
                fallback_data = fallback_response.json()
                return {
                    "brand": fallback_data.get("card_type", "Unknown").upper(),
                    "type": fallback_data.get("card_category", "Unknown").upper(),
                    "level": fallback_data.get("card_level", "Unknown").upper(),
                    "bank": fallback_data.get("issuer", "Unknown"),
                    "country": fallback_data.get("country", "Unknown"),
                    "emoji": "",  # This API does not provide emoji data
                }
        except Exception as e:
            print(f"Error with fallback BIN API: {e}")

        # If all APIs fail, return default "Unknown"
        return {
            "brand": "Unknown",
            "type": "Unknown",
            "level": "Unknown",
            "bank": "Unknown",
            "country": "Unknown",
            "emoji": "",
        }



# Fetch a random anime picture
def fetch_anime_pic():
    try:
        response = requests.get("https://api.waifu.pics/sfw/waifu")
        if response.status_code == 200:
            return response.json().get("url", None)
    except Exception as e:
        print(f"Error fetching anime pic: {e}")
    return "https://i.imgur.com/4Z1sMEx.jpeg"  # Default fallback


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
    bot.send_message(chat_id, " 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 ❣️  𝘾𝙪𝙨𝙩𝙤𝙢𝙞𝙯𝙚 𝙮𝙤𝙪𝙧 𝙗𝙞𝙣 𝘿𝙚𝙩𝙖𝙞𝙡𝙨 𝙝𝙚𝙧𝙚  👇", reply_markup=keyboard)


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

    # Fetch BIN details
    bin_details = fetch_bin_details(bin_prefix)

    # Generate cards
    cards = [generate_card(bin_prefix, month, year, cvv_length, fixed_cvv) for _ in range(quantity)]

    # Fetch an anime picture
    anime_pic = fetch_anime_pic()

    # BIN details summary
    bin_info = (
        f"𝗕𝗜𝗡 ⇾ `{bin_prefix}`\n"
        f"𝗕𝗿𝗮𝗻𝗱 ⇾ {bin_details['brand']}\n"
        f"𝗧𝘆𝗽𝗲 ⇾ {bin_details['type']}\n"
        f"𝗟𝗲𝘃𝗲𝗹 ⇾ {bin_details['level']}\n"
        f"𝗜𝘀𝘀𝘂𝗲𝗿 ⇾ {bin_details['bank']}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {bin_details['country']} {bin_details['emoji']}\n\n"
    )

    cards_output = "\n".join(cards)

    bot.send_photo(
        chat_id,
        photo=anime_pic,
        caption=f"{bin_info} 🔥 𝗛𝗲𝗿𝗲 𝗶𝘀 𝘆𝗼𝘂𝗿 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗖𝗖'𝘀 🔥  :\n\n{cards_output}",
    )


# Start the bot
bot.polling(none_stop=True)
