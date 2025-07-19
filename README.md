# Instagram Post Monitor

A Python application that monitors an Instagram account for new posts and sends notifications with the post image and top comments via Telegram.

## Features

- Continuously monitors a specified Instagram account for new posts
- Retrieves the top 20 comments from each new post
- Sends notifications with the post image and comments via Telegram
- Sleeps for a configurable interval between checks (default: 1 hour)

## Requirements

- Python 3.7+
- Instagram account (optional, for login to avoid rate limits)
- Telegram bot token and chat ID

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/instagram-crawler.git
   cd instagram-crawler
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install the required dependencies:
   ```
   poetry install
   ```

## Configuration

The application is configured using environment variables.

### Environment Variables

Create a `.env` file in the project directory with the following variables:

```
# Instagram configuration
INSTAGRAM_ACCOUNT=instagram_account_to_monitor

# Telegram configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Instagram login (optional)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_TOTP_SECRET=your_instagram_totp_secret

# Monitoring configuration
CHECK_INTERVAL=3600
```

You can copy the `.env.example` file to `.env` and edit it with your values:

```
cp .env.example .env
```

## Usage

After configuring your environment variables in the `.env` file, run the application using Poetry:

```
poetry run python main.py
```

You can also activate the Poetry virtual environment and run the script directly:

```
poetry shell
python main.py
```

## Getting Telegram Token and Chat ID

### Creating a Telegram Bot and Getting the Token

1. Open Telegram and search for "BotFather" or click this link: [BotFather](https://t.me/botfather)
2. Start a chat with BotFather and send the command `/newbot`
3. Follow the instructions to create a new bot:
   - Provide a name for your bot (e.g., "Instagram Monitor")
   - Provide a username for your bot (must end with "bot", e.g., "instagram_monitor_bot")
4. After successful creation, BotFather will provide you with a token that looks like this:
   ```
   123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```
5. Copy this token and use it as your `TELEGRAM_TOKEN` in the `.env` file

### Getting Your Telegram Chat ID

1. Start a chat with your newly created bot by searching for its username
2. Send any message to your bot (e.g., "Hello")
3. Open your web browser and visit this URL (replace `<YOUR_BOT_TOKEN>` with your actual token):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Look for the `"chat":{"id":` field in the JSON response. The number after it is your chat ID.
   It might look like this: `"chat":{"id":123456789}`
5. Copy this number (including the minus sign if it has one) and use it as your `TELEGRAM_CHAT_ID` in the `.env` file

You can also use group chats or channels. For group chats, add your bot to the group and follow the same steps.
For channels, add your bot as an administrator to the channel.

## Instagram Authentication and 2FA

The application uses the Instaloader library to interact with Instagram. If you have Two-Factor Authentication (2FA) enabled on your Instagram account:

### TOTP (Time-based One-Time Password)

This application supports TOTP-based 2FA (using apps like Google Authenticator, Authy, etc.). To use it:

1. **Set up your TOTP secret**:
   - Add your TOTP secret to the `.env` file as `INSTAGRAM_TOTP_SECRET`
   - The secret is the key used to generate the 2FA codes
   - You can find this secret when you initially set up 2FA on your Instagram account
   - If you no longer have access to the secret, you may need to disable and re-enable 2FA on your Instagram account

2. **Format of the TOTP secret**:
   - The secret should be in the base32 format (typically a string of letters and numbers)
   - Example: `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`

3. **If you don't have your TOTP secret**:
   You can try these alternatives:
   - Create a session cookie file:
     - Log in to Instagram in your browser
     - Use a browser extension to export cookies
     - Save the cookies in a format compatible with Instaloader
     - Use the `--sessionfile` parameter with Instaloader
   - Temporarily disable and re-enable 2FA to get a new secret

### SMS-based 2FA

The current implementation does not directly support SMS-based 2FA. If you have SMS-based 2FA enabled on your Instagram account, you may need to:

1. **Switch to TOTP-based 2FA**:
   - Consider switching from SMS-based 2FA to TOTP-based 2FA on your Instagram account
   - This will allow you to use the TOTP support in this application

2. **Use alternative methods**:
   - Create a session cookie file as described in the TOTP section
   - Temporarily disable 2FA on your Instagram account for authentication
   - Use an Instagram account without 2FA for monitoring purposes

## Project Structure

- `models.py`: Data classes for Instagram posts, comments, and Telegram messages
- `instagram_handler.py`: Handler for Instagram operations
- `telegram_handler.py`: Handler for Telegram operations
- `main.py`: Main script that ties everything together

## License

MIT
