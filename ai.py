import requests
import logging
import json
import uuid
import pycountry

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Stripe API Key (Replace with your live key)
API_KEY = "pk_live_8AOKNZetuMq5MDbq6uKUyjDM"  # Use your live Stripe API key

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

def normalize_year(year):
    """Normalize short year format (e.g., '26') to full year format (e.g., '2026')."""
    if len(year) == 2:  # Short year format
        current_century = str(uuid.uuid1().year)[:2]  # Get current century (e.g., '20')
        return f"{current_century}{year}"
    return year

def create_payment_method(cc, cvv, mes, ano, name, email, address, time_on_page):
    """Create a payment method on Stripe."""
    url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0",
    }
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
        "payment_user_agent": "stripe.js/d7f2cc0ba1; stripe-js-v3/d7f2cc0ba1",
        "time_on_page": time_on_page,
        "key": API_KEY,
    }

    try:
        logging.info("Sending request to Stripe API...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
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

def process_card(card_input):
    """
    Process the card input, normalize the year, and validate via Stripe API.
    """
    try:
        # Split and validate the card input
        card_parts = card_input.split("|")
        if len(card_parts) != 4:
            return "❌ Invalid card format. Use `cc|mm|yyyy|cvv`."

        cc, mes, ano, cvv = card_parts
        ano = normalize_year(ano)  # Normalize the year format
        time_on_page = 33381

        # Fetch random user details
        name, email, address = get_random_user()
        if not name or not email or not address:
            return "❌ Failed to generate user details."

        # Call Stripe API
        response = create_payment_method(cc, cvv, mes, ano, name, email, address, time_on_page)
        if response:
            return format_response(response, cc, mes, ano, cvv)
        else:
            return "❌ Card check failed. Please try again."
    except Exception as e:
        logging.error(f"Error processing card: {e}")
        return "❌ An error occurred. Please try again later."
