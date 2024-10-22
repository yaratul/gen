import random
from datetime import datetime
import requests

# Luhn algorithm to ensure the card number is valid
def luhn_generate(bin_number):
    number = [int(digit) for digit in bin_number]
    while len(number) < 15:  # Ensure 15 digits (last will be the check digit)
        number.append(random.randint(0, 9))

    # Calculate the Luhn check digit
    checksum = 0
    for i, digit in enumerate(reversed(number)):
        if i % 2 == 0:  # Double every second digit from the right
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    check_digit = (10 - (checksum % 10)) % 10
    number.append(check_digit)

    return ''.join(map(str, number))

# Generate a random future expiration date (month and year)
def generate_expiry():
    current_year = datetime.now().year
    current_month = datetime.now().month
    year = random.randint(current_year, current_year + 5)  # Generate year from current year to +5 years

    if year == current_year:
        month = random.randint(current_month + 1, 12)  # Ensure the month is in the future
    else:
        month = random.randint(1, 12)

    return f"{month:02}", str(year)

# Generate a random CVC
def generate_cvc():
    return f"{random.randint(100, 999)}"

# Function to generate 25 valid card numbers with the provided BIN, expiry, and CVC
def generate_cards(bin_number, expiry_month=None, expiry_year=None, cvc=None):
    cards = []

    for _ in range(25):
        card_number = luhn_generate(bin_number)  # Generate a valid card number
        
        # Generate random expiry if not provided
        if expiry_month is None or expiry_year is None:
            expiry_month, expiry_year = generate_expiry()

        # Generate random CVC if not provided
        if cvc is None:
            cvc = generate_cvc()

        # Format the card
        card = f"{card_number}|{expiry_month}|{expiry_year}|{cvc}"
        cards.append(card)

    return cards

# BIN Lookup via BINList API
def get_bin_details(bin_number):
    bin_number = bin_number[:6]  # Ensure it's 6 digits

    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if response.status_code == 200:
            bin_data = response.json()
            bin_info = {
                "Bank": bin_data.get("bank", {}).get("name", "Unknown"),
                "Country": bin_data.get("country", {}).get("name", "Unknown"),
                "Card Type": bin_data.get("type", "Unknown"),
            }
        else:
            bin_info = {"Bank": "Unknown", "Country": "Unknown", "Card Type": "Unknown"}
    except Exception as e:
        bin_info = {"Bank": "Unknown", "Country": "Unknown", "Card Type": "Unknown"}
    
    return bin_info

# For testing
if __name__ == "__main__":
    bin_input = "418117"  # Example BIN
    month = None          # Allow random generation
    year = None           # Allow random generation
    cvc = None            # Allow random generation

    generated_cards = generate_cards(bin_input, month, year, cvc)
    bin_info = get_bin_details(bin_input)  # Get BIN info from API

    for card in generated_cards:
        print(card)
    
    print("\nBIN Info:", bin_info)
