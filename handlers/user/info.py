from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()


@router.message(Command("info"))
@router.message(F.text == "ℹ️ Информация")
async def cmd_info(message: types.Message):
    text = """
    📚 <b>Информация о проекте</b>

    Этот бот создан для учебных целей.
    Функционал:
    • Регистрация пользователей
    • Создание заявок
    • Админ-панель
    • Работа с базой данных
    """
    await message.answer(text, parse_mode='HTML')