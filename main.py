import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import gen  # Import the generation tool logic
import px   # Import the proxy checker tool logic
import ai   # Import the AI card checker tool logic

# Replace this with your actual Telegram bot token
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'
bot = telebot.TeleBot(TOKEN)

# List of tools
tools = [
    {"name": "Generate CCs", "callback_data": "tool_generate_ccs"},
    {"name": "Check Proxies", "callback_data": "tool_check_proxies"},
    {"name": "Check Cards", "callback_data": "tool_check_cards"}
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
        # Tool selection logic
        if call.data == "tool_generate_ccs":
            gen.start_gen(bot, call.message)
        elif call.data == "tool_check_proxies":
            start_proxy_checker(bot, call.message)
        elif call.data == "tool_check_cards":
            start_card_checker(bot, call.message)
    elif call.data.startswith("gen_"):
        # Route to gen.py's callback handler
        gen.handle_callbacks(bot, call)

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

    live_proxies = px.validate_proxies(proxies)  # Use the validate_proxies function from px.py

    if live_proxies:
        live_output = "\n".join(live_proxies)
        bot.send_message(chat_id, f"✅ **Live Proxies Found:**\n\n```\n{live_output}\n```", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ No live proxies found.")

# Card Checker Tool Logic
def start_card_checker(bot, message):
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
    Process the card input by the user and validate it using ai.py.
    """
    chat_id = message.chat.id
    card_input = message.text.strip()
    
    # Validate card format
    if not "|" in card_input or len(card_input.split("|")) != 4:
        bot.send_message(chat_id, "❌ Invalid format. Use `cc|mm|yyyy|cvv`.", parse_mode="Markdown")
        return

    try:
        cc, mes, ano, cvv = card_input.split("|")
        time_on_page = 33381

        # Fetch random user details
        name, email, address = ai.get_random_user()
        if not name or not email or not address:
            bot.send_message(chat_id, "❌ Failed to fetch random user details.")
            return

        # Call create_payment_method from ai.py
        result = ai.create_payment_method(cc, cvv, mes, ano, name, email, address, time_on_page, ai.API_KEY)
        if result:
            formatted_response = ai.format_response(result, cc, mes, ano, cvv)
            bot.send_message(chat_id, formatted_response, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "❌ Card check failed. Please try again.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ An error occurred:\n\n`{str(e)}`", parse_mode="Markdown")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
