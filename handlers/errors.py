import logging
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()
logger = logging.getLogger(__name__)

@router.error()
async def error_handler(event: ErrorEvent):
    logger.error("Произошла ошибка", exc_info=event.exception)
    # Здесь можно отправить сообщение об ошибке пользователю или администратору