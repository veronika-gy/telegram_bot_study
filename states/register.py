from aiogram.fsm.state import StatesGroup, State

class RegisterStates(StatesGroup):
    # Шаги регистрации согласно ТЗ
    waiting_for_language = State()
    waiting_for_name = State()      # Шаг 1: Ввод имени
    waiting_for_group = State()     # Шаг 2: Выбор или ввод группы
    waiting_for_phone = State()     # Шаг 3: Ввод телефона (опционально)
    confirmation = State()          # Шаг 4: Подтверждение данных