from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.queries import get_user_by_telegram_id, create_user
from database.db import get_session
from keyboards.user_keyboards import get_main_menu_kb, get_cancel_kb, get_groups_kb
from states.register import RegisterStates

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

    if user:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"С возвращением, {user.name}!\nВыберите действие:",
            reply_markup=get_main_menu_kb()
        )
    else:
        # Начинаем регистрацию
        await message.answer(
            "👋 Привет! Я учебный бот.\nДавай зарегистрируемся!\n\nВведи своё имя:",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(RegisterStates.waiting_for_name)

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отменить")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Действие отменено.",
        reply_markup=get_main_menu_kb()
    )

# ШАГ 1: Получение имени
@router.message(RegisterStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2 or len(name) > 50:
        await message.answer("❌ Имя должно быть от 2 до 50 символов. Попробуй ещё раз:")
        return

    await state.update_data(name=name)

    await message.answer(
        f"👌 Отлично, {name}!\n\n"
        f"Теперь выбери свою учебную группу:",
        reply_markup=get_groups_kb()
    )
    await state.set_state(RegisterStates.waiting_for_group)

# ШАГ 2: Получение группы (через кнопки)
@router.callback_query(RegisterStates.waiting_for_group, F.data.startswith("group_"))
async def process_group_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "group_other":
        await callback.message.answer("Введи название своей группы:")
        return

    group_map = {"group_1": "Группа 1", "group_2": "Группа 2"}
    group = group_map.get(callback.data, "Группа 1")

    await state.update_data(group=group)
    await callback.message.answer(
        f"📋 Группа: {group}\n\n"
        f"Теперь введи свой номер телефона (необязательно):\n"
        f"Можно пропустить, отправив /skip",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(RegisterStates.waiting_for_phone)
    await callback.answer()

# ШАГ 2: Получение группы (текстовый ввод)
@router.message(RegisterStates.waiting_for_group)
async def process_group_text(message: types.Message, state: FSMContext):
    group = message.text.strip()

    if len(group) < 2 or len(group) > 30:
        await message.answer("❌ Название группы должно быть от 2 до 30 символов. Попробуй ещё раз:")
        return

    await state.update_data(group=group)
    await message.answer(
        f"📋 Группа: {group}\n\n"
        f"Теперь введи свой номер телефона (необязательно):\n"
        f"Можно пропустить, отправив /skip",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(RegisterStates.waiting_for_phone)

# ШАГ 3: Пропуск телефона
@router.message(Command("skip"))
@router.message(RegisterStates.waiting_for_phone, F.text == "/skip")
async def skip_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=None)
    await show_confirmation(message, state)

# ШАГ 3: Получение телефона
@router.message(RegisterStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    import re
    phone = message.text.strip()

    phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    if phone and not re.match(phone_pattern, phone):
        await message.answer("❌ Неверный формат телефона. Попробуй ещё раз или отправь /skip:")
        return

    await state.update_data(phone=phone if phone else None)
    await show_confirmation(message, state)


# Функция показа подтверждения
async def show_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if 'name' not in data or 'group' not in data:
        await message.answer(
            "❌ Ошибка: данные не найдены. Начните регистрацию заново через /start",
            reply_markup=get_cancel_kb()
        )
        await state.clear()
        return

    text = (
        f"📋 <b>Проверь данные:</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🎓 Группа: {data['group']}\n"
        f"📞 Телефон: {data.get('phone', 'не указан')}\n\n"
        f"Всё верно?"
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Да, сохранить", callback_data="confirm_yes"),
                types.InlineKeyboardButton(text="❌ Нет, изменить", callback_data="confirm_no")
            ]
        ]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(RegisterStates.confirmation)


# ШАГ 4: Подтверждение - ДА
@router.callback_query(RegisterStates.confirmation, F.data == "confirm_yes")
async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async for session in get_session():
        user = await create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=data['name'],
            group=data['group'],
            phone=data.get('phone')
        )

    await callback.message.answer(
        f"✅ <b>Регистрация завершена!</b>\n\n"
        f"Приветствуем, {data['name']}!\n"
        f"Теперь доступны все функции бота.",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )

    await state.clear()
    await callback.answer()


# ШАГ 4: Подтверждение - НЕТ
@router.callback_query(RegisterStates.confirmation, F.data == "confirm_no")
async def reject_registration(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Начнём регистрацию заново.\n\nВведи своё имя:",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(RegisterStates.waiting_for_name)
    await callback.answer()