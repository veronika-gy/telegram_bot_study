from aiogram.fsm.state import StatesGroup, State

class TicketStates(StatesGroup):
    waiting_for_text = State()  # Ожидание текста заявки
    waiting_for_photo = State() # Ожидание фото (необязательно)