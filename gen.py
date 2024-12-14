import random
from datetime import datetime
import requests

# ----------------------------------------
# Luhn Algorithm: Generate a valid card number
# ----------------------------------------
def luhn_generate(bin_number):
    """
    Generate a valid card number based on the Luhn algorithm.

    :param bin_number: The first 6 digits of the BIN.
    :return: A valid card number.
    """
    if len(bin_number) < 6:
        raise ValueError("BIN must be at least 6 digits.")

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

# ----------------------------------------
# Expiry Date Generator: Unique and future
# ----------------------------------------
def generate_unique_expiry(existing_expiries):
    """
    Generate a unique future expiration date (MM|YYYY).

    :param existing_expiries: Set of already generated expirations to avoid duplicates.
    :return: A unique expiration date in the format (MM, YYYY).
    """
    current_year = datetime.now().year
    current_month = datetime.now().month

    while True:
        year = random.randint(current_year, current_year + 5)
        month = random.randint(1, 12)

        # Ensure the expiration date is not in the current month and is unique
        if not (year == current_year and month == current_month) and (month, year) not in existing_expiries:
            existing_expiries.add((month, year))
            return f"{month:02}", str(year)

# ----------------------------------------
# CVC Generator: Unique for each card
# ----------------------------------------
def generate_cvc(existing_cvc):
    """
    Generate a unique 3-digit CVC.

    :param existing_cvc: Set of already generated CVCs to avoid duplicates.
    :return: A unique CVC.
    """
    while True:
        cvc = f"{random.randint(100, 999)}"
        if cvc not in existing_cvc:
            existing_cvc.add(cvc)
            return cvc

# ----------------------------------------
# Generate Cards: Combining all components
# ----------------------------------------
def generate_cards(bin_number, quantity=25):
    """
    Generate a batch of cards with unique details (MM|YYYY|CVC).

    :param bin_number: The first 6 digits of the BIN.
    :param quantity: Number of cards to generate.
    :return: List of card details in the format CardNumber|MM|YYYY|CVC.
    """
    if len(bin_number) < 6 or not bin_number.isdigit():
        raise ValueError("BIN must be a valid 6-digit number.")

    if quantity < 1 or quantity > 5000:
        raise ValueError("Quantity must be between 1 and 5000.")

    cards = []
    existing_expiries = set()
    existing_cvc = set()

    for _ in range(quantity):
        card_number = luhn_generate(bin_number)  # Generate card number
        expiry_month, expiry_year = generate_unique_expiry(existing_expiries)  # Generate unique expiry
        cvc = generate_cvc(existing_cvc)  # Generate unique CVC
        card = f"{card_number}|{expiry_month}|{expiry_year}|{cvc}"  # Format the card
        cards.append(card)

    return cards

# ----------------------------------------
# BIN Details Lookup via BINList API
# ----------------------------------------
def get_bin_details(bin_number):
    """
    Fetch BIN details (Bank, Country, Card Type) using BINList API.

    :param bin_number: The first 6 digits of the BIN.
    :return: A dictionary of BIN details.
    """
    bin_number = bin_number[:6]

    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if response.status_code == 200:
            bin_data = response.json()
            return {
                "Bank": bin_data.get("bank", {}).get("name", "Unknown"),
                "Country": bin_data.get("country", {}).get("name", "Unknown"),
                "Card Type": bin_data.get("type", "Unknown"),
            }
        else:
            return {"Bank": "Unknown", "Country": "Unknown", "Card Type": "Unknown"}
    except Exception as e:
        print(f"Error fetching BIN details: {e}")
        return {"Bank": "Unknown", "Country": "Unknown", "Card Type": "Unknown"}

# ----------------------------------------
# User-Friendly Output Formatter
# ----------------------------------------
def format_cards_output(cards, bin_info):
    """
    Format card details and BIN information for display.

    :param cards: List of generated cards.
    :param bin_info: Dictionary of BIN details.
    :return: A formatted string for display.
    """
    cards_output = "\n".join(cards[:10])  # Display first 10 cards
    bin_details = (
        f"BIN Details:\n"
        f"Bank: {bin_info['Bank']}\n"
        f"Country: {bin_info['Country']}\n"
        f"Card Type: {bin_info['Card Type']}"
    )
    return f"Generated {len(cards)} cards:\n{cards_output}\n\n{bin_details}"

# ----------------------------------------
# Interactive CLI for Testing
# ----------------------------------------
if __name__ == "__main__":
    print("Welcome to the Ultimate Card Generator!")
    try:
        bin_number = input("Enter the BIN (first 6 digits): ").strip()
        quantity = int(input("Enter the number of cards to generate (1-5000): "))

        # Generate cards
        generated_cards = generate_cards(bin_number, quantity)

        # Fetch BIN details
        bin_info = get_bin_details(bin_number)

        # Display formatted output
        print(format_cards_output(generated_cards, bin_info))

        # Optionally save to file
        save_to_file = input("Save to file? (y/n): ").strip().lower()
        if save_to_file == "y":
            file_name = f"generated_cards_{bin_number}.txt"
            with open(file_name, "w") as file:
                file.write("\n".join(generated_cards))
            print(f"Cards saved to {file_name}.")

    except Exception as e:
        print(f"Error: {e}")
