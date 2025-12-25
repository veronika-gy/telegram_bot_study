from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("admin_tickets"))
async def cmd_admin_tickets(message: types.Message):
    await message.answer("Админ: функционал управления заявками в разработке")