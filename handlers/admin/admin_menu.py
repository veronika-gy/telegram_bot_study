from aiogram import Router, types, F
from aiogram.filters import Command
from config import load_config
from database.db import get_session
from sqlalchemy import select
from database.models import User, Ticket
from keyboards.user_keyboards import get_main_menu_kb

router = Router()
config = load_config()


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    # Проверяем права администратора
    if message.from_user.id not in config.admin_ids:
        await message.answer("⛔ У вас нет прав администратора!")
        return

    # Создаем клавиатуру админ-панели
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👥 Все пользователи")],
            [types.KeyboardButton(text="📋 Все заявки")],
            [types.KeyboardButton(text="📊 Статистика")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🛠️ <b>Админ-панель</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# Обработчик кнопки "👥 Все пользователи"
@router.message(F.text == "👥 Все пользователи")
async def show_all_users(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        return

    async for session in get_session():
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()

        if not users:
            await message.answer("📭 Пользователей пока нет.")
            return

        text = "👥 <b>Все пользователи:</b>\n\n"
        for user in users[:20]:  # Показываем первые 20
            text += (
                f"👤 <b>{user.name}</b>\n"
                f"Telegram ID: {user.telegram_id}\n"
                f"Группа: {user.group}\n"
                f"Телефон: {user.phone if user.phone else 'не указан'}\n"
                f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n"
                f"{'-' * 30}\n"
            )

        await message.answer(text, parse_mode="HTML")


# Обработчик кнопки "📋 Все заявки"
@router.message(F.text == "📋 Все заявки")
async def show_all_tickets(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        return

    async for session in get_session():
        result = await session.execute(select(Ticket).order_by(Ticket.created_at.desc()))
        tickets = result.scalars().all()

        if not tickets:
            await message.answer("📭 Заявок пока нет.")
            return

        text = "📋 <b>Все заявки:</b>\n\n"
        for ticket in tickets[:15]:  # Показываем последние 15 заявок
            # Эмодзи для статуса
            status_icons = {
                'новая': '🆕',
                'в обработке': '🔄',
                'отвечено': '✅',
                'отклонено': '❌'
            }
            icon = status_icons.get(ticket.status, '📄')

            # Обрезаем длинный текст
            ticket_text = ticket.text
            if len(ticket_text) > 40:
                ticket_text = ticket_text[:37] + "..."

            text += (
                f"{icon} <b>Заявка #{ticket.id}</b>\n"
                f"Пользователь ID: {ticket.user_id}\n"
                f"📝 {ticket_text}\n"
                f"📅 {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"📊 Статус: {ticket.status}\n"
                f"{'-' * 30}\n"
            )

        await message.answer(text, parse_mode="HTML")


# Обработчик кнопки "📊 Статистика"
@router.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        return

    async for session in get_session():
        # Считаем пользователей
        users_result = await session.execute(select(User))
        users_count = len(users_result.scalars().all())

        # Считаем заявки
        tickets_result = await session.execute(select(Ticket))
        tickets_count = len(tickets_result.scalars().all())

        # Считаем заявки по статусам
        tickets_all = tickets_result.scalars().all()
        status_counts = {}
        for ticket in tickets_all:
            status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1

        text = (
            f"📊 <b>Статистика бота:</b>\n\n"
            f"👥 Пользователей: <b>{users_count}</b>\n"
            f"📋 Всего заявок: <b>{tickets_count}</b>\n\n"
            f"<b>Заявки по статусам:</b>\n"
        )

        for status, count in status_counts.items():
            text += f"• {status}: {count}\n"

        await message.answer(text, parse_mode="HTML")

        # Обработчик кнопки "🔙 Главное меню"

    @router.message(F.text == "🔙 Главное меню")
    async def back_to_main_menu(message: types.Message):
        await message.answer(
            "🔙 Возвращаемся в главное меню...",
            reply_markup=get_main_menu_kb()
        )