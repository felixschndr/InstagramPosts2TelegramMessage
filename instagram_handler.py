import logging
import os
from datetime import datetime
from typing import Optional

import pyotp
from instagrapi import Client

from models import InstagramComment, InstagramPost


class InstagramHandler:
    """Handler for Instagram operations."""

    def __init__(self, target_account: str):
        """
        Initialize the Instagram handler.

        Args:
            target_account: The Instagram account to monitor
        """
        self.target_account = target_account
        self.client = Client()
        self.last_post_id = None
        self.last_post_timestamp = None
        self.logger = logging.getLogger(__name__)
        # Use absolute path to ensure file is created in the root directory
        self.last_post_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_post_info.txt")

        # Load last post info from file if it exists
        self._load_last_post_info()

    def _load_last_post_info(self):
        """
        Load the last post information from the file.
        """
        try:
            if os.path.exists(self.last_post_file):
                with open(self.last_post_file, "r") as f:
                    lines = f.readlines()
                    if len(lines) >= 1:
                        self.last_post_id = lines[0].strip()
                        self.logger.info(f"Loaded last post ID: {self.last_post_id}")
                    if len(lines) >= 2:
                        # Try to parse the timestamp from the second line
                        try:
                            timestamp_str = lines[1].strip()
                            self.last_post_timestamp = datetime.fromisoformat(timestamp_str)
                            self.logger.info(f"Loaded last post timestamp: {self.last_post_timestamp}")
                        except ValueError:
                            # If the timestamp can't be parsed, it's just for human reading
                            self.logger.warning(f"Could not parse timestamp: {lines[1].strip()}")
        except Exception as e:
            self.logger.error(f"Error loading last post info: {str(e)}")

    def _save_last_post_info(self, post_id, timestamp):
        """
        Save the last post information to the file.

        Args:
            post_id: The ID of the last post
            timestamp: The timestamp of the last post
        """
        try:
            with open(self.last_post_file, "w") as f:
                f.write(f"{post_id}\n")
                # Add a human-readable timestamp
                human_readable = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{human_readable}\n")
            self.logger.info(f"Saved last post info: ID={post_id}, timestamp={human_readable}")
        except Exception as e:
            self.logger.error(f"Error saving last post info: {str(e)}")

    def login(self, username: str, password: str, totp_secret: Optional[str] = None) -> bool:
        """
        Login to Instagram (optional but recommended to avoid rate limits).

        Args:
            username: Instagram username
            password: Instagram password
            totp_secret: TOTP secret for two-factor authentication (optional)

        Returns:
            True if login successful, False otherwise
        """
        try:
            # If TOTP secret is provided, generate TOTP code
            verification_code = None
            if totp_secret:
                totp = pyotp.TOTP(totp_secret)
                verification_code = totp.now()
                self.logger.info(f"Generated TOTP code for 2FA: {verification_code}")

            # Login with or without 2FA
            self.client.login(username, password, verification_code=verification_code)
            self.logger.info(f"Logged in as {username}")
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def get_new_posts(self) -> list[InstagramPost]:
        """
        Get new posts from the target account.

        Returns:
            List of new InstagramPost objects
        """
        try:
            # Get user ID from username
            user_id = self.client.user_id_from_username(self.target_account)
            # Get user's media (posts)
            media_items = self.client.user_medias(user_id, 20)  # Get the 20 most recent posts
            posts = []
            newest_post_id = None
            newest_post_timestamp = None

            for media in media_items:
                # Convert timestamp to datetime
                created_at = datetime.fromtimestamp(media.taken_at)

                # If we've seen this post before (by ID), skip
                if self.last_post_id and media.id == self.last_post_id:
                    self.logger.debug(f"Skipping already processed post: {media.id}")
                    break

                # If we've seen posts newer than this one, skip
                if self.last_post_timestamp and created_at <= self.last_post_timestamp:
                    self.logger.debug(f"Skipping older post: {media.id}, {created_at}")
                    continue

                # Track the newest post we've seen
                if newest_post_timestamp is None or created_at > newest_post_timestamp:
                    newest_post_id = media.id
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

            # Update the last post info if we found new posts
            if newest_post_id and (not self.last_post_id or newest_post_id != self.last_post_id):
                self.last_post_id = newest_post_id
                self.last_post_timestamp = newest_post_timestamp
                self._save_last_post_info(newest_post_id, newest_post_timestamp)

            self.logger.info(f"Found {len(posts)} new posts")
            return posts

        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            return []

    def get_top_comments(self, media) -> list[InstagramComment]:
        """
        Get the top 20 comments from a post.

        Args:
            media: The Instagram media object from instagrapi

        Returns:
            List of InstagramComment objects
        """
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
            self.logger.error(f"Error fetching comments: {str(e)}")
            return []
