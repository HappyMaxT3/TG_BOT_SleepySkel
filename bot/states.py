from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    group = State()
    sleep_start = State()
    sleep_end = State()
