from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from bot.keyboards import create_dynamic_menu
from bot.states import Form
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.inline_handlers import router as inline_router 
from bot.storage import save_user_name, get_user_name, save_sleep_start, save_sleep_event, get_sleep_start, save_sleep_end
from aiogram.filters.state import State, StatesGroup

class SleepCorrection(StatesGroup):
    waiting_for_correct_time = State()

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

async def notify_after_10_hours(user_id: int, sleep_start: str, bot: Bot):
    await asyncio.sleep(10 * 60 * 60)

    current_sleep_start = get_sleep_start(user_id)
    if current_sleep_start == sleep_start:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "💀⏳ It's been 10 hours since you marked the start of your sleep.\n"
                "If you are awake, please mark the end of your sleep! 🛏️"
            ),
            reply_markup=create_dynamic_menu(user_id)
        )

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
    sleep_start_str = f"{current_date} {current_time}"
    save_sleep_start(user_id, sleep_start_str)

    await message.answer(f"🛌 Sleep start recorded: {current_time} {current_date}.", reply_markup=create_dynamic_menu(user_id))
    await state.update_data(button_text="Mark the end of sleep")
    await message.answer(f"💤 Sweet dreams, {name}! Don't forget to mark the end when you wake up!", reply_markup=create_dynamic_menu(user_id))
    
    asyncio.create_task(notify_after_10_hours(user_id, sleep_start_str, message.bot))

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

    total_minutes = sleep_duration.total_seconds() / 60
    if total_minutes < 20:
        save_sleep_start(user_id, None)
        await message.answer(
            f"❌ Sleep duration is too short ({int(total_minutes)} min). Sleep record discarded.",
            reply_markup=create_dynamic_menu(user_id)
        )
        return

    total_hours = sleep_duration.total_seconds() / 3600
    if total_hours > 20:
        await message.answer(
            f"‼️ Sleep duration is too long ({total_hours:.2f} hours). Please provide the correct wake-up time in 'HH:MM' format or type 'cancel' to discard this sleep record.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(SleepCorrection.waiting_for_correct_time)
        await state.update_data(start_datetime=start_datetime)
        return

    hours = sleep_duration.seconds // 3600
    minutes = (sleep_duration.seconds // 60) % 60
    duration_str = f"{hours} H {minutes} Min"
    
    save_sleep_end(user_id, f"{current_date} {current_time}", duration_str)

    await message.answer(
        f"🥱 Sleep start:   {start_datetime.strftime('%H:%M    %Y-%m-%d')}\n"
        f"⏰ Sleep end:     {end_datetime.strftime('%H:%M    %Y-%m-%d')}\n\n"
        f"⏳ Sleep duration: {duration_str}\n",
        reply_markup=create_dynamic_menu(user_id)
    )
    await message.answer(f"🛏️ Sleep is over! {name}, did you sleep well?")
    await state.update_data(button_text="Mark the beginning of sleep")
    await message.answer(f"💀 Mark the beginning of the sleep when you are ready to take a nap!", reply_markup=create_dynamic_menu(user_id))

@router.message(SleepCorrection.waiting_for_correct_time)
async def handle_correct_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text.strip()
    
    if user_input.lower() == "cancel":
        await message.answer("❌ Sleep record discarded.", reply_markup=create_dynamic_menu(user_id))
        await state.clear()
        return

    try:
        corrected_time = datetime.strptime(user_input, "%H:%M").time()
        data = await state.get_data()
        start_datetime = data["start_datetime"]
    
        end_datetime = datetime.combine(start_datetime.date(), corrected_time)
        if end_datetime < start_datetime:
            end_datetime = end_datetime.replace(day=start_datetime.day + 1)
        
        sleep_duration = end_datetime - start_datetime

        hours = sleep_duration.seconds // 3600
        minutes = (sleep_duration.seconds // 60) % 60
        duration_str = f"{hours} H {minutes} Min"
        
        save_sleep_end(user_id, end_datetime.strftime("%Y-%m-%d %H:%M"), duration_str)

        await message.answer(
            f"✅ Corrected sleep recorded:\n\n"
            f"🥱 Sleep start:   {start_datetime.strftime('%H:%M    %Y-%m-%d')}\n"
            f"⏰ Sleep end:     {end_datetime.strftime('%H:%M    %Y-%m-%d')}\n\n"
            f"⏳ Sleep duration: {duration_str}\n",
            reply_markup=create_dynamic_menu(user_id)
        )
        await state.clear()
    except ValueError:
        await message.answer("❗ Invalid time format. Please use 'HH:MM' or type 'cancel'.")

@router.message(F.text == "Show options")
async def show_options_handler(message: Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="option_1")],
        [InlineKeyboardButton(text="📜 Sleep History", callback_data="option_2")],
        [InlineKeyboardButton(text="Cancel", callback_data="cancel")]
    ])
    await message.answer("💀 Choose an option below:", reply_markup=inline_keyboard)

router.include_router(inline_router)  
