from core import check_card, bin_lookup, load_proxies

# Load proxies
proxies = load_proxies('proxies.txt')

# List of allowed users (replace with actual user IDs)
ALLOWED_USERS = [1517013110, 5537383735, 1405151206]  # Add authorized user IDs here


def handle_chk(bot, message):
    """Handles the /chk command."""
    try:
        # Extract the card details
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /chk card_number|mm|yy|cvv")
            return

        card_details = args[1]
        card_number, exp_month, exp_year, cvc = card_details.split('|')

        # Perform BIN lookup
        bin_details = bin_lookup(card_number, proxies)
        if not bin_details:
            bot.reply_to(message, "BIN Lookup Failed. Please try again.")
            return

        # Call check_card without BIN lookup, since it's already performed
        payment_response = check_card(card_number, exp_month, exp_year, cvc, proxies)

        # Format the response
        result = f"""
Response: {payment_response}

𝗖𝗮𝗿𝗱: {card_number}|{exp_month}|{exp_year}|{cvc}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲: Stripe Auth + 1$ charge

𝗜𝗻𝗳𝗼: {bin_details['scheme']} - {bin_details['type']} - {bin_details['brand']}
𝐈𝐬𝐬𝐮𝐞𝐫: {bin_details['bank']}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {bin_details['country']} {bin_details['emoji']}


"""
        # Send the response back to the user
        bot.reply_to(message, result.strip())

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /chk card_number|mm|yy|cvv")


def handle_mchk(bot, message):
    """Handles the /mchk command with live updates."""
    if message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        card_details = message.text[5:].strip()

        if not card_details:
            bot.reply_to(message, "No card details provided. Usage: /mchk card_number|mm|yy|cvv (one per line)")
            return

        card_list = card_details.split('\n')

        max_cards = 25
        if len(card_list) > max_cards:
            card_list = card_list[:max_cards]

        # Send initial processing message
        msg = bot.reply_to(message, "Processing...\n")

        result = ""
        for index, card_info in enumerate(card_list, start=1):
            card_info = card_info.strip()
            if card_info:
                card_number, exp_month, exp_year, cvc = card_info.split('|')

                # Call check_card without BIN lookup
                response = check_card(card_number, exp_month, exp_year, cvc, proxies)

                # Append the response to the result
                result += f"{card_info}\n- {response}\n\n"

                # Update the message after each response
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Processing...\n\n{result.strip()}")

        # Final message update
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Results:\n\n{result.strip()}")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /mchk card_number|mm|yy|cvv (one per line)")

