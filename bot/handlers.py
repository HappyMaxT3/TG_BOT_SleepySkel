from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from .keyboards import create_main_menu
from .states import Form
from .storage import save_user_name, get_user_name, save_sleep_start, save_sleep_end

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    if name:
        await message.answer(f"С возвращением, {name}!", reply_markup=create_main_menu())
    else:
        await message.answer("Добро пожаловать! Введите ваше имя:")
        await state.set_state(Form.name)

@router.message(Form.name)
async def handle_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_user_name(user_id, message.text)
    await message.answer(f"Имя сохранено, {message.text}!", reply_markup=create_main_menu())
    await state.clear()

@router.message(F.text == "Сменить имя")
async def change_name_handler(message: Message, state: FSMContext):
    await message.answer("Введите новое имя:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

@router.message(F.text == "Начало сна")
async def sleep_start_handler(message: Message, state: FSMContext):
    await message.answer("Введите время начала сна (в формате HH:MM):")
    await state.set_state(Form.sleep_start)

@router.message(Form.sleep_start)
async def handle_sleep_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_sleep_start(user_id, message.text)
    await message.answer("Время начала сна сохранено!", reply_markup=create_main_menu())
    await state.clear()

@router.message(F.text == "Конец сна")
async def sleep_end_handler(message: Message, state: FSMContext):
    await message.answer("Введите время конца сна (в формате HH:MM):")
    await state.set_state(Form.sleep_end)

@router.message(Form.sleep_end)
async def handle_sleep_end(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_sleep_end(user_id, message.text)
    await message.answer("Время конца сна сохранено!", reply_markup=create_main_menu())
    await state.clear()
