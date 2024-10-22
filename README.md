
---

# Card Generator Bot

## Overview

This project includes two Python scripts that work together to generate valid credit card numbers based on the **Luhn algorithm** and validate the information using the **BIN lookup**. The card generation logic is powered by the **Luhn algorithm**, and BIN information is retrieved using the **BINList API**. The main script is a **Telegram bot** that allows users to interactively generate card details by providing minimal information, such as the BIN (Bank Identification Number).

### Features:
- Generate **25 valid card numbers** at once.
- Supports card generation using a **6-digit BIN** or more user-supplied details such as expiration month/year and CVC.
- Automatically generates **future expiration dates** and random **CVC** if not provided.
- Displays **BIN details** such as bank name, country, and card type.
- Cards are returned in a **monospace format** (for easy copying) in Telegram.

## Files

1. **gen.py**:
   - Implements the **Luhn algorithm** to generate valid card numbers.
   - Provides functions for **generating random expiration dates** and **CVC**.
   - Fetches **BIN details** via the [BINList API](https://binlist.net/).

2. **main.py**:
   - Implements the **Telegram bot** using the `telebot` library.
   - Users can interact with the bot using the `/gen` command to generate card numbers.
   - Sends **25 generated card numbers** along with BIN information in a **monospace block** for easy copying.

## Prerequisites

Before running the scripts, ensure you have the following installed:

```bash
pip install pyTelegramBotAPI
pip install requests
```

## How to Use

### Setting Up the Bot

1. **Telegram Bot Setup**:
   - Create a new Telegram bot by messaging [BotFather](https://t.me/BotFather) and get your API token.
   - Replace the placeholder `YOUR_BOT_TOKEN_HERE` in `main.py` with your actual bot token.

2. **Run the Bot**:
   - Start the bot by running `main.py`.

```bash
python main.py
```

### Bot Commands

#### /gen Command

Use the `/gen` command to generate cards. You can provide either just the BIN or additional details (expiration date, CVC):

- **Basic Command (BIN only)**:
  - `/gen 418117`
  - This generates 25 valid card numbers with random expiration dates and CVC.
  
- **Full Command (BIN, month, year, CVC)**:
  - `/gen 418117|12|2028|123`
  - This generates 25 card numbers using the specified BIN, expiration date, and CVC.

### Output Format

The bot will return 25 generated card numbers in a **monospace format** for easy copying:

```
𝙇𝙪𝙝𝙣 𝘼𝙣𝙙 𝙍𝙚𝙜𝙚𝙭 𝙑𝙚𝙧𝙞𝙛𝙞𝙚𝙙 ✅
418117xxxxxxxxxx|12|2028|123
418117xxxxxxxxxx|12|2028|123
...

BIN Details:
Bank: [Bank Name]
Country: [Country Name]
Card Type: [Card Type]
```

### Error Handling

If the input format is incorrect, the bot will respond with:
```
𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙤𝙧𝙢𝙖𝙩. 𝙐𝙨𝙚: /𝙜𝙚𝙣 𝘽𝙄𝙉|𝙈𝙈|𝙔𝙔𝙔𝙔|𝘾𝙑𝘾 𝙤𝙧 𝙨𝙞𝙢𝙥𝙡𝙮 /𝙜𝙚𝙣 𝘽𝙄𝙉
```

## Notes

- Ensure your bot is **running on a server** or **locally** with a stable internet connection to interact with the Telegram API and the BINList API.
- The generated card numbers are **not real** and should only be used for testing purposes in compliance with legal standards.

## Disclaimer

This tool is intended for **educational purposes only**. The author is not responsible for any illegal or unethical use of this tool. Always comply with your local laws and regulations when using tools like this.

---
