import asyncio
from datetime import timedelta

from environment_variable_getter import EnvironmentVariableGetter
from instagram_handler import InstagramHandler
from logger_mixin import LoggerMixin
from telegram_handler import TelegramHandler


class InstagramMonitor(LoggerMixin):
    def __init__(self):
        super().__init__()

        self.instagram_handler = InstagramHandler()
        self.telegram_handler = TelegramHandler()

        self.check_interval = timedelta(seconds=int(EnvironmentVariableGetter.get("CHECK_INTERVAL", 3600)))

    def start(self) -> None:
        self.log.info(f"Starting to monitor Instagram account: {self.instagram_handler.target_account}")

        self.instagram_handler.login()

        asyncio.run(self.run_loop())

    async def run_loop(self) -> None:
        """Run the main monitoring loop."""
        while True:
            try:
                new_posts = self.instagram_handler.get_new_posts()

                if not new_posts:
                    self.log.info("No new posts found")
                else:
                    for post in new_posts:
                        self.log.info(f"New post found: {post.url}")
                        success = await self.telegram_handler.notify_new_post(post)
                        if success:
                            self.log.info(f"Notification sent for post: {post.url}")
                        else:
                            self.log.error(f"Failed to send notification for post: {post.url}")

            except Exception as e:
                self.log.error(f"Error in monitoring loop: {str(e)}")

            # Sleep for the specified interval
            self.log.info(f"Sleeping for {self.check_interval.total_seconds()} seconds")
            await asyncio.sleep(self.check_interval.total_seconds())


if __name__ == "__main__":
    monitor = InstagramMonitor()
    monitor.start()
