from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from .storage import get_sleep_start

def create_dynamic_menu(user_id):
    sleep_start = get_sleep_start(user_id)
    
    if sleep_start:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Mark the end of sleep")],
                [KeyboardButton(text="Change the name")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Mark the beginning of sleep")],
                [KeyboardButton(text="Change the name")]
            ],
            resize_keyboard=True
        )
