from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.queries import create_ticket, get_tickets_by_user, get_user_by_telegram_id
from database.db import get_session
from keyboards.user_keyboards import get_main_menu_kb, get_cancel_kb
from states.ticket import TicketStates
import logging

router = Router()
logger = logging.getLogger(__name__)


# Обработчик для кнопки "🎫 Оставить заявку" и команды /tickets
@router.message(Command("tickets"))
@router.message(F.text == "🎫 Оставить заявку")
async def cmd_create_ticket(message: types.Message, state: FSMContext):
    # Проверяем, зарегистрирован ли пользователь
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    await message.answer(
        "📝 <b>Создание заявки</b>\n\n"
        "Опишите вашу проблему или вопрос:\n"
        "(Можно прикрепить фото в следующем сообщении)",
        parse_mode="HTML",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(TicketStates.waiting_for_text)


# Получение текста заявки
@router.message(TicketStates.waiting_for_text)
async def process_ticket_text(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("❌ Текст заявки должен содержать минимум 5 символов. Попробуйте ещё раз:")
        return

    await state.update_data(text=message.text.strip())

    await message.answer(
        "📎 Хотите прикрепить фото к заявке?\n"
        "Отправьте фото или нажмите кнопку 'Пропустить'",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📎 Пропустить фото")],
                [types.KeyboardButton(text="❌ Отменить")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(TicketStates.waiting_for_photo)


# Пропуск фото через кнопку
@router.message(TicketStates.waiting_for_photo, F.text == "📎 Пропустить фото")
async def skip_photo_button(message: types.Message, state: FSMContext):
    await save_ticket(message, state, photo=None)


# Получение фото
@router.message(TicketStates.waiting_for_photo, F.photo)
async def process_ticket_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await save_ticket(message, state, photo=photo_id)


# Основная функция сохранения заявки
async def save_ticket(message: types.Message, state: FSMContext, photo: str = None):
    # Получаем данные из состояния
    data = await state.get_data()
    ticket_text = data.get('text', '')

    if not ticket_text:
        await message.answer("❌ Ошибка: текст заявки не найден.", reply_markup=get_main_menu_kb())
        await state.clear()
        return

    # Получаем пользователя
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

        if not user:
            await message.answer("❌ Пользователь не найден.", reply_markup=get_main_menu_kb())
            await state.clear()
            return

        # Создаем заявку
        try:
            ticket = await create_ticket(
                session=session,
                user_id=user.id,
                text=ticket_text,
                photo=photo
            )

            await message.answer(
                f"✅ <b>Заявка #{ticket.id} создана!</b>\n\n"
                f"Статус: {ticket.status}\n"
                f"Дата: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )

        except Exception as e:
            await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_main_menu_kb())

    await state.clear()

# Просмотр моих заявок
@router.message(F.text == "📋 Мои заявки")
async def cmd_my_tickets(message: types.Message):
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start")
            return

        tickets = await get_tickets_by_user(session, user.id)

        if not tickets:
            await message.answer("📭 У вас пока нет заявок.")
            return

        response = "📋 <b>Ваши заявки:</b>\n\n"
        for ticket in tickets[:10]:
            status_emoji = {
                'новая': '🆕',
                'в обработке': '🔄',
                'отвечено': '✅',
                'отклонено': '❌'
            }.get(ticket.status, '📄')

            response += (
                f"{status_emoji} <b>Заявка #{ticket.id}</b>\n"
                f"📝 {ticket.text[:50]}...\n"
                f"📅 {ticket.created_at.strftime('%d.%m.%Y')}\n"
                f"📊 Статус: {ticket.status}\n"
                f"{'-' * 30}\n"
            )

        await message.answer(response, parse_mode="HTML")


# Отмена создания заявки
@router.message(TicketStates.waiting_for_text)
@router.message(TicketStates.waiting_for_photo)
async def cancel_ticket(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer(
            "❌ Создание заявки отменено.",
            reply_markup=get_main_menu_kb()
        )