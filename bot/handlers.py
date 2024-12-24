from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from .keyboards import create_dynamic_menu
from .states import Form
from .storage import save_user_name, get_user_name, save_sleep_start, save_sleep_end, get_sleep_start, get_sleep_end

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    if name:
        await message.answer(f"С возвращением, {name}!", reply_markup=create_dynamic_menu(user_id))
    else:
        await message.answer("Добро пожаловать! Введите ваше имя:")
        await state.set_state(Form.name)

@router.message(Form.name)
async def handle_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_user_name(user_id, message.text)
    await message.answer(f"Имя сохранено, {message.text}!", reply_markup=create_dynamic_menu(user_id))
    await state.clear()

@router.message(F.text == "Сменить имя")
async def change_name_handler(message: Message, state: FSMContext):
    await message.answer("Введите новое имя:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

@router.message(F.text == "Начало сна")
async def sleep_start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    sleep_start = get_sleep_start(user_id)
    
    if sleep_start:
        await message.answer("Вы уже записали время начала сна. Сначала завершите текущий сон, а затем можете записать новое начало сна.", reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    save_sleep_start(user_id, current_time)
    await message.answer(f"Время начала сна записано: {current_time}", reply_markup=create_dynamic_menu(user_id))

@router.message(F.text == "Конец сна")
async def sleep_end_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    sleep_start = get_sleep_start(user_id)
    
    if not sleep_start:
        await message.answer("Сначала запишите время начала сна перед записью конца сна.", reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    save_sleep_end(user_id, current_time)
    await message.answer(f"Время конца сна записано: {current_time}", reply_markup=create_dynamic_menu(user_id))

    save_sleep_start(user_id, '')
    await message.answer("Вы завершили сон! Ждем новой записи начала сна!", reply_markup=create_dynamic_menu(user_id))
