import requests

def check_vbv(card_input):
    """
    Check the VBV status of a card using the provided API.
    """
    try:
        # API endpoint
        url = f"https://easilypay.co.uk/v1/api.php?lista={card_input}"

        # Headers for the request
        headers = {
            'authority': 'easilypay.co.uk',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'origin': 'https://www.trickadsagencyltd.com',
            'referer': 'https://www.trickadsagencyltd.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }

        # Send the request
        response = requests.get(url, headers=headers)
        response_data = response.json()

        # Parse the response
        if response_data.get("success"):
            status = response_data["data"]["status"]
            bank_info = response_data["data"]["bank_info"]
            return f"𝗩𝗕𝗩 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n𝗕𝗮𝗻𝗸 𝗜𝗻𝗳𝗼: {bank_info}"
        else:
            return "Error: Failed to check VBV status."

    except Exception as e:
        return f"Error: {str(e)}"
