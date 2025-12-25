from aiogram import Router, types, F
from aiogram.filters import Command
from database.queries import get_user_by_telegram_id
from database.db import get_session

router = Router()


@router.message(Command("profile"))
@router.message(F.text == "👤 Мой профиль")
async def cmd_profile(message: types.Message):
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

    if user:
        text = (f"📋 <b>Ваш профиль</b>\n\n"
                f"👤 Имя: {user.name}\n"
                f"🎓 Группа: {user.group}\n"
                f"📞 Телефон: {user.phone if user.phone else 'не указан'}\n"
                f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}")
        await message.answer(text, parse_mode='HTML')
    else:
        await message.answer("Вы не зарегистрированы. Введите /start")