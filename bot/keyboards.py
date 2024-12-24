from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def create_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начало сна")],
            [KeyboardButton(text="Конец сна")],
            [KeyboardButton(text="Сменить имя")]
        ],
        resize_keyboard=True
    )
