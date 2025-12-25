from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("users"))
async def cmd_users(message: types.Message):
    await message.answer("Админ: функционал управления пользователями в разработке")