from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (Reply клавиатура, появляется снизу)
def get_main_menu_kb():
    buttons = [
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="ℹ️ Информация")],
        [KeyboardButton(text="🎫 Оставить заявку"), KeyboardButton(text="📋 Мои заявки")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Клавиатура для отмены действия
def get_cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отменить")]], resize_keyboard=True)

# Inline-кнопки для выбора группы при регистрации
def get_groups_kb():
    buttons = [
        [InlineKeyboardButton(text="Группа 1", callback_data="group_1")],
        [InlineKeyboardButton(text="Группа 2", callback_data="group_2")],
        [InlineKeyboardButton(text="Другая", callback_data="group_other")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)