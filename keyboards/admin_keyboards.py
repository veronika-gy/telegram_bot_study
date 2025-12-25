from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню администратора
def get_admin_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="📋 Список заявок", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для управления заявкой (смена статуса, ответ)
def get_ticket_management_kb(ticket_id: int):
    buttons = [
        [InlineKeyboardButton(text="✅ Отвечено", callback_data=f"ticket_answer_{ticket_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"ticket_reject_{ticket_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)