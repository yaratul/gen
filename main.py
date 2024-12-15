import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import gen  # Import the generation tool logic
import px   # Import the proxy checker tool logic

# Replace this with your actual Telegram bot token
TOKEN = '6126045919:AAEo-9ddN2PvlzWtnWtyUbkxQCUpSyXLKVg'
bot = telebot.TeleBot(TOKEN)

# List of tools
tools = [
    {"name": "Generate CCs", "callback_data": "tool_generate_ccs"},
    {"name": "Check Proxies", "callback_data": "tool_check_proxies"}
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
    elif call.data.startswith("gen_"):
        # Route to gen.py's callback handler
        gen.handle_callbacks(bot, call)

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

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
