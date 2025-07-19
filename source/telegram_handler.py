import logging

from telegram import Bot
from telegram.error import TelegramError

from source.environment_variable_getter import EnvironmentVariableGetter
from source.models import InstagramPost, TelegramMessage


class TelegramHandler:
    """Handler for Telegram operations."""

    def __init__(self):
        """
        Initialize the Telegram handler.

        Args:
            token: Telegram bot token
        """
        self.bot = Bot(token=EnvironmentVariableGetter.get("TELEGRAM_TOKEN"))
        self.target_chat_id = EnvironmentVariableGetter.get("TELEGRAM_TARGET_CHAT_ID")
        self.logger = logging.getLogger(__name__)

    async def send_message(self, message: TelegramMessage) -> bool:
        """
        Send a message to a Telegram chat.

        Args:
            message: TelegramMessage object containing chat_id, text, and optional image_url

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            if message.image_url:
                # Send message with image
                await self.bot.send_photo(chat_id=message.chat_id, photo=message.image_url, caption=message.text)
            else:
                # Send text-only message
                await self.bot.send_message(chat_id=message.chat_id, text=message.text)

            self.logger.info(f"Message sent to chat {message.chat_id}")
            return True

        except TelegramError as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False

    def create_post_message(self, post: InstagramPost) -> TelegramMessage:
        # Create message text with post caption and comments
        text = f"New post from {post.url}\n\n"

        if post.caption:
            text += f"Caption: {post.caption}\n\n"

        if post.comments:
            text += "Top comments:\n"
            for i, comment in enumerate(post.comments, 1):
                text += f"{i}. @{comment.username}: {comment.text}\n"

        # Create TelegramMessage object
        return TelegramMessage(chat_id=self.target_chat_id, text=text, image_url=post.image_url)

    async def notify_new_post(self, post: InstagramPost) -> bool:
        message = self.create_post_message(post, self.target_chat_id)
        return await self.send_message(message)
