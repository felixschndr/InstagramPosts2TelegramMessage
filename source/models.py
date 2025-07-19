from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class InstagramComment:
    """Dataclass to store Instagram comment information."""

    id: str
    text: str
    username: str
    created_at: datetime


@dataclass
class InstagramPost:
    """Dataclass to store Instagram post information."""

    id: str
    url: str
    image_url: str
    caption: Optional[str]
    created_at: datetime
    comments: List[InstagramComment]


@dataclass
class TelegramMessage:
    """Dataclass to store Telegram message information."""

    chat_id: str
    text: str
    image_url: Optional[str] = None
