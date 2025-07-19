import os
from datetime import datetime

import pyotp
from instagrapi import Client
from instagrapi.types import Media

from source.environment_variable_getter import EnvironmentVariableGetter
from source.logger_mixin import LoggerMixin
from source.models import InstagramComment, InstagramPost


class InstagramHandler(LoggerMixin):
    def __init__(self):
        super().__init__()

        self.target_account = EnvironmentVariableGetter.get("INSTAGRAM_TARGET_ACCOUNT")
        self.client = Client()

        self.last_timestamp = self._load_last_post_info()
        self.last_post_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_post_info.txt")

    def login(self) -> None:
        self.log.info("Trying to login...")
        verification_code = None
        totp_secret = EnvironmentVariableGetter.get("INSTAGRAM_TOTP_SECRET", None)
        if totp_secret:
            totp = pyotp.TOTP(totp_secret)
            verification_code = totp.now()
            self.log.info(f"Generated TOTP code for 2FA: {verification_code}")

        self.client.login(
            EnvironmentVariableGetter.get("INSTAGRAM_USERNAME"),
            EnvironmentVariableGetter.get("INSTAGRAM_PASSWORD"),
            verification_code=verification_code,
        )
        self.log.info("Logged in")

    def get_new_posts(self) -> list[InstagramPost]:
        try:
            user_id = self.client.user_id_from_username(self.target_account)
            media_items = self.client.user_medias(user_id, 20)
            posts = []
            newest_post_timestamp = None

            for media in media_items:
                created_at = media.taken_at

                if created_at < self.last_timestamp:
                    self.log.debug(f"Skipping old post: {media.id} (from {created_at})")
                    continue

                # Track the newest post we've seen
                if newest_post_timestamp is None or created_at > newest_post_timestamp:
                    newest_post_timestamp = created_at

                # Get comments for this post
                comments = self.get_top_comments(media)

                # Get the URL of the first image in the post
                image_url = media.thumbnail_url

                # Create InstagramPost object
                instagram_post = InstagramPost(
                    id=media.id,
                    url=f"https://www.instagram.com/p/{media.code}/",
                    image_url=image_url,
                    caption=media.caption_text if media.caption_text else "",
                    created_at=created_at,
                    comments=comments,
                )

                posts.append(instagram_post)

            self._save_last_post_info(newest_post_timestamp)

            self.log.info(f"Found {len(posts)} new posts")
            return posts

        except Exception as e:
            self.log.error(f"Error fetching posts: {str(e)}")
            return []

    def get_top_comments(self, media: Media) -> list[InstagramComment]:
        try:
            comments = []

            # Get comments for the media
            media_comments = self.client.media_comments(media.id, 20)  # Get up to 20 comments

            for comment in media_comments:
                instagram_comment = InstagramComment(
                    id=str(comment.pk),
                    text=comment.text,
                    username=comment.user.username,
                    created_at=datetime.fromtimestamp(comment.created_at),
                )

                comments.append(instagram_comment)

            return comments

        except Exception as e:
            self.log.error(f"Error fetching comments: {str(e)}")
            return []

    def _load_last_post_info(self) -> datetime:
        if not os.path.exists(self.last_post_file):
            return datetime.fromtimestamp(0)

        with open(self.last_post_file, "r") as f:
            lines = f.readlines()
            last_timestep = datetime.fromisoformat(lines[0].strip())
            self.log.info(f"Last seen post was from {last_timestep}")
            return last_timestep

    def _save_last_post_info(self, newest_post_timestamp: datetime) -> None:
        try:
            with open(self.last_post_file, "w") as f:
                f.write(newest_post_timestamp.isoformat())
            self.log.info(f"Saved newest seen post timestamp ({newest_post_timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        except Exception as e:
            self.log.error(f"Error saving last post info: {str(e)}")
