import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from database.db import create_db
from handlers.user import start, profile, info, tickets, help
from handlers.admin import admin_menu, users, tickets as admin_tickets
from handlers import errors


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    config = load_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация БД
    await create_db()

    # Подключаем роутеры (обработчики команд)
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(info.router)
    dp.include_router(tickets.router)
    dp.include_router(help.router)
    dp.include_router(admin_menu.router)
    dp.include_router(users.router)
    dp.include_router(admin_tickets.router)
    dp.include_router(errors.router)


    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())