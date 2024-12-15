import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import gen  # Import the generation tool logic

# Replace this with your actual Telegram bot token
TOKEN = '6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU'
bot = telebot.TeleBot(TOKEN)

# List of tools
tools = [
    {"name": "Generate CCs", "callback_data": "tool_generate_ccs"}
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
    elif call.data.startswith("gen_"):
        # Route to gen.py's callback handler
        gen.handle_callbacks(bot, call)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
