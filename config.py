import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN")
    admin_ids: List[int] = field(default_factory=list)
    db_name: str = os.getenv("DB_NAME", "database.db")


def load_config() -> Config:
    config = Config()

    # Преобразуем строку из .env в список чисел
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        config.admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

    return config