import random
import re
import requests
from datetime import datetime

def get_random_proxy(proxies):
    """ Select a random proxy from the list. """
    proxy = random.choice(proxies)
    ip_port, credentials = proxy.split('@')
    proxy_url = f"http://{credentials}@{ip_port}"
    return {
        "http": proxy_url,
        "https": proxy_url,
    }

def fetch_bin_info(bin_number, proxies):
    """
    Fetch BIN details using a free API and proxy support.
    """
    api_url = f"https://lookup.binlist.net/{bin_number}"
    headers = {"Accept-Version": "3"}

    proxy = get_random_proxy(proxies)  # Get a random proxy for the request
    try:
        response = requests.get(api_url, headers=headers, proxies=proxy, timeout=10)

        if response.status_code == 200:
            data = response.json()
            brand = data.get('scheme', 'Unknown').upper()
            type_ = data.get('type', 'Unknown').upper()
            level = data.get('brand', 'Unknown').upper()
            bank = data.get('bank', {}).get('name', 'Unknown')
            country = data.get('country', {}).get('name', 'Unknown')
            emoji = data.get('country', {}).get('emoji', '')
            return f"{brand} - {type_} - {level}\n𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {emoji}"
        else:
            print(f"BIN Lookup Failed: {response.status_code} - {response.text}")
            return "Failed to fetch BIN details."
    except requests.RequestException as e:
        print(f"BIN Lookup Error: {e}")
        return "Failed to fetch BIN details."

def luhn_algorithm(bin_prefix, length=16):
    """
    Generate a valid card number using the Luhn algorithm.
    """
    card_number = [int(x) for x in bin_prefix if x.isdigit()]
    while len(card_number) < (length - 1):
        card_number.append(random.randint(0, 9))

    checksum = 0
    reversed_digits = card_number[::-1]
    for i, digit in enumerate(reversed_digits):
        if i % 2 == 0:
            double = digit * 2
            checksum += double - 9 if double > 9 else double
        else:
            checksum += digit

    last_digit = (10 - (checksum % 10)) % 10
    card_number.append(last_digit)
    return ''.join(map(str, card_number))

def generate_expiry_date(constant_month=None, constant_year=None):
    """
    Generate a random expiry date in MM/YYYY format, ensuring it is not expired.
    """
    current_year = datetime.now().year
    current_month = datetime.now().month

    year = constant_year or random.randint(current_year, current_year + 10)
    if year == current_year:
        month = constant_month or random.randint(current_month, 12)
    else:
        month = constant_month or random.randint(1, 12)

    return f"{month:02d}", year

def generate_cvv(constant_cvv=None, card_type="VISA"):
    """
    Generate a random CVV/CVC based on card type or use a constant CVV if provided.
    """
    if constant_cvv:
        return constant_cvv
    if card_type == "AMEX":
        return f"{random.randint(1000, 9999)}"
    return f"{random.randint(100, 999)}"

def parse_input(bin_input):
    """
    Parse the user's input for constants.
    """
    match = re.match(r"(\d+)(?:\|(\d{2}))?(?:\|(\d{4}|\d{2}))?(?:\|(\d+))?", bin_input)
    if not match:
        return None, None, None, None

    card_bin = match.group(1)
    constant_month = int(match.group(2)) if match.group(2) else None
    constant_year = int(match.group(3)) if match.group(3) else None
    if constant_year and constant_year < 100:  # Handle 2-digit years
        constant_year += 2000
    constant_cvv = match.group(4)

    return card_bin, constant_month, constant_year, constant_cvv

def generate_cards(bin_input, amount=25, proxies=None):
    """
    Generate a list of valid cards based on the given BIN and constants.
    """
    card_bin, constant_month, constant_year, constant_cvv = parse_input(bin_input)

    if not card_bin or len(card_bin) < 6:
        return "Error: BIN must be at least 6 digits."

    bin_prefix = card_bin[:6]
    cards = []
    bin_info = fetch_bin_info(bin_prefix, proxies)  # Pass proxies to the fetch_bin_info function

    for _ in range(amount):
        card_number = luhn_algorithm(card_bin)
        month, year = generate_expiry_date(constant_month, constant_year)
        cvv = generate_cvv(constant_cvv)
        cards.append(f"{card_number}|{month}|{year}|{cvv}")

    return cards, bin_info
