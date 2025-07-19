import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from instagram_handler import InstagramHandler
from telegram_handler import TelegramHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class InstagramMonitor:
    """Main class to monitor Instagram posts and send notifications."""

    def __init__(
        self,
        instagram_account: str,
        telegram_token: str,
        telegram_chat_id: str,
        instagram_username: Optional[str] = None,
        instagram_password: Optional[str] = None,
        instagram_totp_secret: Optional[str] = None,
        check_interval: int = 3600,  # 1 hour in seconds
    ):
        """
        Initialize the Instagram monitor.

        Args:
            instagram_account: Instagram account to monitor
            telegram_token: Telegram bot token
            telegram_chat_id: Telegram chat ID to send notifications to
            instagram_username: Instagram username for login (optional)
            instagram_password: Instagram password for login (optional)
            instagram_totp_secret: Instagram TOTP secret for 2FA (optional)
            check_interval: Interval between checks in seconds (default: 1 hour)
        """
        self.instagram_handler = InstagramHandler(instagram_account)
        self.telegram_handler = TelegramHandler(telegram_token)
        self.telegram_chat_id = telegram_chat_id
        self.check_interval = check_interval
        self.instagram_username = instagram_username
        self.instagram_password = instagram_password
        self.instagram_totp_secret = instagram_totp_secret

    def start(self):
        """Start monitoring Instagram posts."""
        logger.info(f"Starting to monitor Instagram account: {self.instagram_handler.target_account}")

        # Login to Instagram if credentials are provided
        if self.instagram_username and self.instagram_password:
            success = self.instagram_handler.login(
                self.instagram_username, self.instagram_password, self.instagram_totp_secret
            )
            if not success:
                logger.warning("Instagram login failed. Continuing without login.")

        # Run the main loop
        asyncio.run(self.run_loop())

    async def run_loop(self):
        """Run the main monitoring loop."""
        while True:
            try:
                # Check for new posts
                new_posts = self.instagram_handler.get_new_posts()

                # Send notifications for new posts
                for post in new_posts:
                    logger.info(f"New post found: {post.url}")
                    success = await self.telegram_handler.notify_new_post(post, self.telegram_chat_id)
                    if success:
                        logger.info(f"Notification sent for post: {post.url}")
                    else:
                        logger.error(f"Failed to send notification for post: {post.url}")

                # If no new posts were found, log it
                if not new_posts:
                    logger.info("No new posts found")

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

            # Sleep for the specified interval
            logger.info(f"Sleeping for {self.check_interval} seconds")
            await asyncio.sleep(self.check_interval)


def get_config():
    """Get configuration from environment variables."""
    config = {
        "instagram_account": os.getenv("INSTAGRAM_ACCOUNT"),
        "telegram_token": os.getenv("TELEGRAM_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "instagram_username": os.getenv("INSTAGRAM_USERNAME"),
        "instagram_password": os.getenv("INSTAGRAM_PASSWORD"),
        "instagram_totp_secret": os.getenv("INSTAGRAM_TOTP_SECRET"),
        "check_interval": int(os.getenv("CHECK_INTERVAL", "3600")),
    }

    return config


if __name__ == "__main__":
    # Get configuration from environment variables
    config = get_config()

    # Validate required environment variables
    if not config["instagram_account"]:
        logger.error("Instagram account is required. Set INSTAGRAM_ACCOUNT environment variable.")
        exit(1)

    if not config["telegram_token"]:
        logger.error("Telegram bot token is required. Set TELEGRAM_TOKEN environment variable.")
        exit(1)

    if not config["telegram_chat_id"]:
        logger.error("Telegram chat ID is required. Set TELEGRAM_CHAT_ID environment variable.")
        exit(1)

    # Create and start the monitor
    monitor = InstagramMonitor(
        instagram_account=config["instagram_account"],
        telegram_token=config["telegram_token"],
        telegram_chat_id=config["telegram_chat_id"],
        instagram_username=config["instagram_username"],
        instagram_password=config["instagram_password"],
        instagram_totp_secret=config["instagram_totp_secret"],
        check_interval=config["check_interval"],
    )

    monitor.start()
