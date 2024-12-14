import random

def generate_luhn_compliant_card(bin_prefix):
    """
    Generates a Luhn-compliant card number starting with the provided BIN prefix.
    Args:
        bin_prefix (str): The BIN prefix (minimum 6 digits).
    Returns:
        str: A valid card number.
    """
    # Fill the card number up to 15 digits (excluding the check digit)
    card_number = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(15 - len(bin_prefix))])

    # Calculate the Luhn checksum
    total_sum = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 0:  # Double every second digit (from right)
            n *= 2
            if n > 9:
                n -= 9
        total_sum += n

    # Calculate the check digit
    check_digit = (10 - (total_sum % 10)) % 10
    return card_number + str(check_digit)

def generate_batch(bin_prefix, quantity):
    """
    Generates a batch of valid card numbers.
    Args:
        bin_prefix (str): The BIN prefix (minimum 6 digits).
        quantity (int): The number of card numbers to generate.
    Returns:
        list: A list of valid card numbers.
    """
    if len(bin_prefix) < 6 or not bin_prefix.isdigit():
        raise ValueError("BIN prefix must be at least 6 digits.")
    if not (1 <= quantity <= 50):
        raise ValueError("Quantity must be between 1 and 50.")

    card_numbers = []
    for _ in range(quantity):
        card_numbers.append(generate_luhn_compliant_card(bin_prefix))
    return card_numbers

# For standalone testing
if __name__ == "__main__":
    test_bin = "479851"  # Example BIN prefix
    num_cards = 10       # Example quantity
    generated_cards = generate_batch(test_bin, num_cards)
    print("\n".join(generated_cards))
