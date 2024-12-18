import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import gen  # Import Generate CCs tool
import px   # Import Proxy Checker tool
import ai   # Import Card Checker tool

# Telegram Bot Token
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'  # Replace with your bot token
bot = telebot.TeleBot(TOKEN)

# List of tools
tools = [
    {"name": "Generate CCs", "callback_data": "tool_generate_ccs"},
    {"name": "Check Proxies", "callback_data": "tool_check_proxies"},
    {"name": "Check Cards", "callback_data": "tool_check_cards"}
]

# ========================== Bot Handlers ==========================

@bot.message_handler(commands=['start'])
def start(message):
    """
    Show tool options to the user.
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
        keyboard.add(InlineKeyboardButton(tool["name"], callback_data=tool["callback_data"]))
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """
    Handle callback data for tools.
    """
    if call.data.startswith("tool_"):
        # Tool selection routing
        if call.data == "tool_generate_ccs":
            gen.start_gen(bot, call.message)
        elif call.data == "tool_check_proxies":
            start_proxy_checker(bot, call.message)
        elif call.data == "tool_check_cards":
            start_card_checker(bot, call.message)
    elif call.data.startswith("gen_"):
        # Route to gen.py's callback handler
        gen.handle_callbacks(bot, call)

# ========================== Proxy Checker ==========================

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

    live_proxies = px.validate_proxies(proxies)  # Use px.py's validate_proxies function

    if live_proxies:
        live_output = "\n".join(live_proxies)
        bot.send_message(chat_id, f"✅ **Live Proxies Found:**\n\n```\n{live_output}\n```", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ No live proxies found.")

# ========================== Card Checker ==========================

def start_card_checker(bot, message):
    """
    Start the Card Checker tool and prompt the user for card input.
    """
    msg = bot.send_message(
        message.chat.id,
        "📥 Send the card details to check:\n\nFormat: `cc|mm|yyyy|cvv` or `cc|mm|yy|cvv`",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_card_check)

@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda message: message.text.startswith('.chk'))
def card_check_command(message):
    """
    Handle /chk and .chk commands.
    """
    card_input = message.text.split(maxsplit=1)[-1] if " " in message.text else None
    if card_input:
        process_card_check(message, card_input)
    else:
        bot.reply_to(message, "❌ Please provide card details in the correct format:\n\n`cc|mm|yyyy|cvv`", parse_mode="Markdown")

def process_card_check(message, card_input=None):
    """
    Process the card input by the user.
    """
    chat_id = message.chat.id
    card_input = card_input or message.text.strip()

    # Call the process_card function from ai.py
    result = ai.process_card(card_input)
    bot.send_message(chat_id, result, parse_mode="Markdown")

# ========================== Run the Bot ==========================

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
