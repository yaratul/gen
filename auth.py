
import requests
import uuid
import pycountry


# Stripe API Key (replace with your live key)
API_KEY = "pk_live_8AOKNZetuMq5MDbq6uKUyjDM"


def create_payment_method(cc, cvv, mm, yyyy, name, email, address):
    """
    Create a payment method on Stripe.

    Args:
        cc (str): Card number.
        cvv (str): Card CVV.
        mm (str): Card expiry month.
        yyyy (str): Card expiry year.
        name (str): User's name.
        email (str): User's email address.
        address (dict): User's address.

    Returns:
        dict: Stripe API response or error details.
    """
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
        "card[exp_month]": mm,
        "card[exp_year]": yyyy,
        "guid": str(uuid.uuid4()),
        "muid": str(uuid.uuid4()),
        "sid": str(uuid.uuid4()),
        "payment_user_agent": "stripe.js",
        "referrer": "https://example.com",
        "key": API_KEY,
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "response": e.response.json() if e.response else None}


def format_response(response, card_details):
    """
    Format the Stripe API response for user-friendly output.

    Args:
        response (dict): Stripe API response.
        card_details (str): Original card details provided.

    Returns:
        str: Formatted response.
    """
    if not response or "card" not in response:
        error = response.get("error", "Unknown error occurred.")
        return f"Failed to check card.\nError: {error}"

    card = response["card"]
    brand = card.get("brand", "Unknown")
    funding = card.get("funding", "Unknown")
    card_type = response.get("type", "Unknown")
    country = card.get("country", "Unknown")
    secure_status = "Accepted" if not card["three_d_secure_usage"]["supported"] else "3D Secure Required"

    return (
        f"===== Card Details =====\n"
        f"{card_details}\n"
        f"Brand: {brand}\n"
        f"Funding Type: {funding}\n"
        f"Type: {card_type}\n"
        f"Country: {country}\n"
        f"3D Secure Supported: {card['three_d_secure_usage']['supported']}\n"
        f"Status: {secure_status}\n"
        f"========================"
    )


def validate_card_input(card_input):
    """
    Validate the card input format.

    Args:
        card_input (str): Card details in the format card_number|mm|yyyy|cvc.

    Returns:
        tuple: Parsed card details or None if invalid.
    """
    try:
        parts = card_input.split("|")
        if len(parts) != 4:
            return None
        card_number, mm, year, cvc = parts

        # Validate card number
        if len(card_number) != 16 or not card_number.isdigit():
            return None

        # Validate month
        if not (1 <= int(mm) <= 12):
            return None

        # Normalize year (convert 2-digit year to 4-digit year)
        if len(year) == 2:
            year = f"20{year}"
        if len(year) != 4 or not year.isdigit():
            return None

        # Validate CVC
        if len(cvc) not in [3, 4]:
            return None

        return card_number, mm, year, cvc
    except ValueError:
        return None
