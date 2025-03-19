import requests

def b3_auth(cc_input):
    """
    Perform BrainTree Auth using the provided card number or full card details.
    """
    try:
        # Extract the card number if full card details are provided
        if "|" in cc_input:
            cc_number = cc_input.split("|")[0]
        else:
            cc_number = cc_input

        # Validate the card number
        if not cc_number.isdigit() or len(cc_number) < 15 or len(cc_number) > 16:
            return "Error: Invalid card number."

        # Send request to BrainTree Auth API
        url = f"https://darkboy-b3.onrender.com/key=dark/cc={cc_number}"
        response = requests.get(url)

        if response.status_code == 200:
            return f"𝗕𝗥𝗔𝗜𝗡𝗧𝗥𝗘𝗘 𝗔𝗨𝗧𝗛 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘:\n\n{response.text}"
        else:
            return f"Error: Failed to fetch response. Status Code: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"
