# InstagramPosts2TelegramMessage

A Python application that monitors an Instagram account for new posts and sends notifications with the post image and top comments via Telegram.

> [!NOTE]  
> This is a proof of concept and not a finished project. It is provided as-is for demonstration purposes.

## Features

- Continuously monitor a specified Instagram account for new posts
- Retrieve the top 5 comments from each new post
- Send notifications with the post image and comments via Telegram
- Sleep for a configurable interval between checks (default: 1 hour)
- Track the last seen post to avoid duplicate notifications
- Supports Two-Factor Authentication (TOTP) for Instagram login

## Requirements

- Python 3.13
- Instagram account (for login)
- Telegram bot token and chat ID (See instructions on how to create such a bot below)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/felixschndr/InstragramPosts2TelegramMessage.git
   cd InstragramPosts2TelegramMessage
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install the required dependencies:
   ```
   poetry install
   ```

4. Run the application
   ```
   python source/main.py
   ```

## Configuration

The application is configured using environment variables.

### Environment Variables

Create a `.env` file in the project directory with the following variables:

```
# Instagram configuration
INSTAGRAM_TARGET_ACCOUNT=instagram_account_to_monitor

# Telegram configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_TARGET_CHAT_ID=your_telegram_chat_id

# Instagram login
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_TOTP_SECRET=your_instagram_totp_secret

# Monitoring configuration
CHECK_INTERVAL=3600

# Logging configuration
LOGLEVEL=INFO
```


The application also supports an optional `.env.override` file that can be used to override values in the `.env` file.

## Usage

After configuring your environment variables in the `.env` file, run the application:

```
python source/main.py
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
2. Open your web browser and visit this URL (replace `<YOUR_BOT_TOKEN>` with your actual token):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Send any message to your bot (e.g., "Hello")
4. Refresh the page in your browser
5. Look for the `"chat":{"id":` field in the JSON response. The number after it is your chat ID.
   It might look like this: `"chat":{"id":123456789}`
6. Copy this number (including the minus sign if it has one) and use it as your `TELEGRAM_CHAT_ID` in the `.env` file

You can also use group chats or channels. For group chats, add your bot to the group and follow the same steps.
For channels, add your bot as an administrator to the channel.

## Instagram Authentication and 2FA

The application uses the Instagrapi library to interact with Instagram. If you have Two-Factor Authentication (2FA) enabled on your Instagram account:

### TOTP (Time-based One-Time Password)

This application supports TOTP-based 2FA (using apps like Google Authenticator, Authy, etc.). To use it:

- Add your TOTP secret to the `.env` file as `INSTAGRAM_TOTP_SECRET` (Example: `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`)
- The secret is the key used to generate the 2FA codes
- You can find this secret when you initially set up 2FA on your Instagram account

## License

MIT
