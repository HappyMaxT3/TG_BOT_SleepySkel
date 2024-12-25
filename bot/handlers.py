from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from bot.keyboards import create_dynamic_menu
from bot.states import Form
from bot.storage import save_user_name, get_user_name, save_sleep_start, save_sleep_event, get_sleep_start, save_sleep_end

# Создаем экземпляр роутера
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    if name:
        await message.answer(f"💀 Welcome back, {name}!", reply_markup=create_dynamic_menu(user_id))
    else:
        await message.answer("💀 Welcome! I`m Sleepy Skel! What should I call you?")
        await state.set_state(Form.name)

@router.message(Form.name)
async def handle_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_user_name(user_id, message.text)
    await message.answer(f"💀 Great, {message.text}!", reply_markup=create_dynamic_menu(user_id))
    await state.clear()

@router.message(F.text == "Change the name")
async def change_name_handler(message: Message, state: FSMContext):
    await message.answer("💀 What should I call you now?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

@router.message(F.text == "Mark the beginning of sleep")
async def sleep_start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    
    sleep_start = get_sleep_start(user_id)
    if sleep_start:
        await message.answer("‼️ You already recorded a sleep start time. Finish the current sleep first.", reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")
    save_sleep_start(user_id, f"{current_date} {current_time}")
    await message.answer(f"🛌 Sleep start recorded: {current_time}  {current_date}.", reply_markup=create_dynamic_menu(user_id))
    await state.update_data(button_text="Mark the end of sleep")
    await message.answer(f"Now, get some sleep and mark the end later.\n💤 Sweet dreams, {name}!\n", reply_markup=create_dynamic_menu(user_id))

@router.message(F.text == "Mark the end of sleep")
async def sleep_end_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    
    sleep_start = get_sleep_start(user_id)
    if not sleep_start:
        await message.answer("‼️ Mark the sleep start before marking the end.", reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    start_datetime = datetime.strptime(sleep_start, "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{current_date} {current_time}", "%Y-%m-%d %H:%M")
    sleep_duration = end_datetime - start_datetime
    hours = sleep_duration.seconds // 3600
    minutes = (sleep_duration.seconds // 60) % 60

    duration_str = f"{hours} H {minutes} Min"
    save_sleep_end(user_id, f"{current_date} {current_time}", duration_str)

    await message.answer(
        f"Sleep start:   {start_datetime.strftime('%H:%M    %Y-%m-%d')}\n"
        f"Sleep end:     {end_datetime.strftime('%H:%M  %Y-%m-%d')}\n"
        f"Sleep duration: {duration_str}\n",
        reply_markup=create_dynamic_menu(user_id)
    )
    await message.answer(f"🛏️ Sleep is over! {name}, did you sleep well?")
    await state.update_data(button_text="Mark the beginning of sleep")
    await message.answer(f"💀 Mark the beginning of the sleep when you are ready to take a nap!", reply_markup=create_dynamic_menu(user_id))
