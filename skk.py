
import stripe

def fetch_stripe_details(api_key):
    """
    Fetch detailed information from a Stripe secret key.
    """
    stripe.api_key = api_key
    details = {}

    try:
        # Fetch account details
        account = stripe.Account.retrieve()
        details["account"] = {
            "Business Name": account.get("business_profile", {}).get("name", "N/A"),
            "Email": account.get("email", "N/A"),
            "Country": account.get("country", "N/A"),
            "Payouts Enabled": account.get("payouts_enabled", "N/A"),
            "Details Submitted": account.get("details_submitted", "N/A"),
        }

        # Fetch balance details
        balance = stripe.Balance.retrieve()
        details["balance"] = {
            "Available": [
                {"Currency": b.get("currency"), "Amount": b.get("amount") / 100}
                for b in balance.get("available", [])
            ],
            "Pending": [
                {"Currency": b.get("currency"), "Amount": b.get("amount") / 100}
                for b in balance.get("pending", [])
            ],
        }

        # Fetch customer details
        customers = stripe.Customer.list(limit=5)  # Fetch up to 5 customers
        details["customers"] = [
            {
                "Name": customer.get("name", "N/A"),
                "Email": customer.get("email", "N/A"),
                "Phone": customer.get("phone", "N/A"),
                "Created At": customer.get("created", "N/A"),
            }
            for customer in customers.get("data", [])
        ]

        # Fetch subscription details
        subscriptions = stripe.Subscription.list(limit=5)  # Fetch up to 5 subscriptions
        details["subscriptions"] = [
            {
                "ID": sub.get("id", "N/A"),
                "Status": sub.get("status", "N/A"),
                "Start Date": sub.get("start_date", "N/A"),
                "Customer ID": sub.get("customer", "N/A"),
            }
            for sub in subscriptions.get("data", [])
        ]

        # Fetch payment method details
        payment_methods = stripe.PaymentMethod.list(type="card", limit=5)
        details["payment_methods"] = [
            {
                "Card Brand": pm.get("card", {}).get("brand", "N/A"),
                "Last 4": pm.get("card", {}).get("last4", "N/A"),
                "Expiry": f"{pm.get('card', {}).get('exp_month', 'N/A')}/"
                          f"{pm.get('card', {}).get('exp_year', 'N/A')}",
            }
            for pm in payment_methods.get("data", [])
        ]

    except stripe.error.AuthenticationError:
        return "Error: Invalid Stripe API key."
    except Exception as e:
        return f"An error occurred: {str(e)}"

    return details


if __name__ == "__main__":
    # Example usage
    stripe_key = input("Enter your Stripe Secret Key (sk_live...): ")
    results = fetch_stripe_details(stripe_key)
    if isinstance(results, str):
        print(results)
    else:
        for section, info in results.items():
            print(f"\n{section.upper()}:\n")
            for key, value in info.items() if isinstance(info, dict) else enumerate(info):
                print(f"{key}: {value}")
