import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import gen  # Import the generation tool logic
import px   # Import the proxy checker tool logic
import auth  # Import the card checker tool logic (formerly ai.py)

# Replace this with your actual Telegram bot token
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'
bot = telebot.TeleBot(TOKEN)

# List of tools
tools = [
    {"name": "Generate CCs", "callback_data": "tool_generate_ccs"},
    {"name": "Check Proxies", "callback_data": "tool_check_proxies"},
    {"name": "Check Cards", "callback_data": "tool_check_cards"},
]

# Handle /start command
@bot.message_handler(commands=['start'])
def start(message):
    """
    Start command to show the tool list in a card design.
    """
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "👋 **Welcome to the Ultimate Tool Bot!**\n\nChoose a tool below to get started:",
        reply_markup=create_tool_keyboard(),
        parse_mode="Markdown"
    )

def create_tool_keyboard():
    """
    Create a keyboard with available tools.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tool in tools:
        keyboard.add(
            InlineKeyboardButton(tool["name"], callback_data=tool["callback_data"])
        )
    return keyboard

# Handle callback data for tools
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """
    Central callback handler for all tools.
    """
    if call.data.startswith("tool_"):
        if call.data == "tool_generate_ccs":
            gen.start_gen(bot, call.message)
        elif call.data == "tool_check_proxies":
            start_proxy_checker(bot, call.message)
        elif call.data == "tool_check_cards":
            start_card_checker(bot, call.message)

# Proxy Checker Tool Logic
def start_proxy_checker(bot, message):
    """
    Start the Proxy Checker tool and prompt the user for proxy input.
    """
    msg = bot.send_message(
        message.chat.id,
        "📥 Send your proxies (one per line):\n\nFormat:\n- `ip:port`\n- `ip:port:username:password`",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_proxies)

def process_proxies(message):
    """
    Process the proxies input by the user.
    """
    chat_id = message.chat.id
    proxies = message.text.strip().split('\n')
    bot.send_message(chat_id, "⏳ Checking proxies... This might take a while.")

    live_proxies = px.validate_proxies(proxies)

    if live_proxies:
        live_output = "\n".join(live_proxies)
        bot.send_message(chat_id, f"✅ **Live Proxies Found:**\n\n```\n{live_output}\n```", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ No live proxies found.")

# Card Checker Tool Logic
@bot.message_handler(commands=['chk', '.chk'])
def start_card_checker(message):
    """
    Start the Card Checker tool and prompt the user for card input.
    """
    msg = bot.send_message(
        message.chat.id,
        "📥 Send the card details (one card per message):\n\nFormat: `cc|mm|yyyy|cvv`",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_card_check)

def process_card_check(message):
    """
    Process the card input by the user and validate it using auth.py.
    """
    chat_id = message.chat.id
    card_input = message.text.strip()
    
    # Validate card format
    card_details = auth.validate_card_input(card_input)
    if not card_details:
        bot.send_message(chat_id, "❌ Invalid format. Use `cc|mm|yyyy|cvv`.", parse_mode="Markdown")
        return

    cc, mm, yyyy, cvv = card_details

    # Static fallback user info
    name, email, address = "Test User", "testuser@example.com", {
        "line1": "123 Test St",
        "city": "Testville",
        "state": "TS",
        "postal_code": "12345",
        "country": "US",
    }

    bot.send_message(chat_id, "⏳ Checking card, please wait...")
    response = auth.create_payment_method(cc, cvv, mm, yyyy, name, email, address)
    formatted_response = auth.format_response(response, card_input)

    bot.send_message(chat_id, formatted_response, parse_mode="Markdown")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
