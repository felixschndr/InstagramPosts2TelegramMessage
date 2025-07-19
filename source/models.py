from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import HttpUrl


@dataclass
class InstagramComment:
    id: str
    text: str
    username: str
    created_at: datetime


@dataclass
class InstagramPost:
    id: str
    url: str
    image_url: HttpUrl
    caption: Optional[str]
    created_at: datetime
    comments: List[InstagramComment]


@dataclass
class TelegramMessage:
    chat_id: str
    text: str
    image_url: Optional[str] = None
