from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from bot.keyboards import create_dynamic_menu
from bot.states import Form
from bot.inline_handlers import router as inline_router 
from bot.storage import (
    save_user_name, get_user_name, save_sleep_start,
    get_sleep_start, save_sleep_end
)
from aiogram.filters.state import State, StatesGroup
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from bot.translator import translate_message
from bot.translator import set_user_language
from aiogram.types import CallbackQuery

class SleepCorrection(StatesGroup):
    waiting_for_correct_time = State()

scheduler = AsyncIOScheduler()

router = Router()

@router.message(Command("set_language"))
async def set_language_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")]
    ])
    await message.answer("💀 Please select your language:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected_language = callback.data.split("_")[1]

    set_user_language(user_id, selected_language)

    language_name = "English" if selected_language == "en" else "Русский"
    await callback.message.answer(f"💀 Language set to {language_name}!", reply_markup=create_dynamic_menu(user_id))
    await callback.answer()

async def send_feedback_prompt(user_id: int, bot: Bot):
    await bot.send_message(user_id, "💀 I remind that you can leave a feedback!\n📝 Just write a message with `feedback` and it will be recordered.")

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    if name:
        await message.answer(f"💀 Welcome back, {name}! Type /info to check my capabilities!", reply_markup=create_dynamic_menu(user_id))
    else:
        await message.answer("💀 Welcome! I`m Sleepy Skel! What should I call you?")
        await state.set_state(Form.name)

    bot = message.bot
    scheduler.add_job(
        send_feedback_prompt, 
        trigger=IntervalTrigger(hours=45),
        args=[user_id, bot],
        max_instances=1
    )
    scheduler.start()

@router.message(Command("info"))
async def info_handler(message: Message):
    part1 = (
        "💀 <b>Sleepy Skel Bot User Guide:</b>\n\n"
        "1️⃣ /start — Start the bot and set up your username.\n"
        "2️⃣ /info — Info and instruction.\n"
        "3️⃣ /set_language — Choose the bot language.\n"
        "4️⃣ 'Mark the beginning of sleep' — Mark the start of sleep.\n"
        "5️⃣ 'Mark the end of sleep' — Mark the end of sleep (sleep duration must be >20 min).\n6️⃣ "
    )
    part2 = (
        " 'Show options' — Show additional settings: statistics, sleep history, chat with SleepySkel.\n"
        "7️⃣ 'Change the name' — Change your name in the bot.\n\n"
        "💡 <b>Tip:</b> Don’t forget to mark the end of sleep to get accurate statistics! 💤\n"
        "If you sleep for more than 10 hours, SleepySkel will remind you to finish recording your sleep. 🛏️\n\n"
        "📝 You can leave feedback! Just send a message with <code>feedback</code> and it will be recorded.\n"
    )
    part3 = (
        "<code>(Feedback It is so cool bot! I really enjoy it! (Waiting 100$ on my PayPal for good reference))</code>"
    )

    translated_text1 = translate_message(part1, message.from_user.id)
    translated_text2 = translate_message(part2, message.from_user.id)
    translated_text = translated_text1 + translated_text2 + part3

    await message.answer(translated_text, parse_mode="HTML")

@router.message(Form.name)
async def handle_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_user_name(user_id, message.text)
    text = f"💀 Great, {message.text}! Type /info to check my capabilities!"
    translated_text = translate_message(text, message.from_user.id)
    await message.answer(translated_text, reply_markup=create_dynamic_menu(user_id))
    await state.clear()

@router.message(F.text == "Change the name")
async def change_name_handler(message: Message, state: FSMContext):
    text = "💀 What should I call you now?"
    await message.answer(translate_message(text, message.from_user.id), reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

async def notify_after_10_hours(user_id: int, sleep_start: str, bot):
    await asyncio.sleep(10 * 60 * 60)
    current_sleep_start = get_sleep_start(user_id)
    if current_sleep_start == sleep_start:
        text = "💀⏳ It's been 10 hours since you marked the start of your sleep.\nIf you are awake, please mark the end of your sleep! 🛏️"
        await bot.send_message(
            chat_id=user_id,
            text=translate_message(text, message.from_user.id),
            reply_markup=create_dynamic_menu(user_id)
        )

@router.message(F.text == "Mark the beginning of sleep")
async def sleep_start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    sleep_start = get_sleep_start(user_id)
    
    if sleep_start:
        text = "‼️ You already recorded a sleep start time. Finish the current sleep first."
        await message.answer(translate_message(text, message.from_user.id), reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")
    sleep_start_str = f"{current_date} {current_time}"
    save_sleep_start(user_id, sleep_start_str)

    text1 = f"💀🛌 Sleep start recorded: {current_time} {current_date}."
    text2 = f"💀💤 Sweet dreams, {name}! Don't forget to mark the end when you wake up!\n(Remember that the minimum sleep duration is 20 minutes)"

    await message.answer(translate_message(text1, message.from_user.id), reply_markup=create_dynamic_menu(user_id))
    await message.answer(translate_message(text2, message.from_user.id), reply_markup=create_dynamic_menu(user_id))

    asyncio.create_task(notify_after_10_hours(user_id, sleep_start_str, message.bot))

@router.message(F.text == "Mark the end of sleep")
async def sleep_end_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    sleep_start = get_sleep_start(user_id)
    
    if not sleep_start:
        text = "‼️ Mark the sleep start before marking the end."
        await message.answer(translate_message(text1, message.from_user.id), reply_markup=create_dynamic_menu(user_id))
        return

    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")

    start_datetime = datetime.strptime(sleep_start, "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{current_date} {current_time}", "%Y-%m-%d %H:%M")
    sleep_duration = end_datetime - start_datetime

    total_minutes = sleep_duration.total_seconds() / 60

    if total_minutes < 20:
        text = f"❌ Sleep duration is too short ({int(total_minutes)} min less than 20 min). Please try again after a longer rest."
        await message.answer(
            translate_message(text, message.from_user.id),
            reply_markup=create_dynamic_menu(user_id)
        )
        return

    total_hours = sleep_duration.total_seconds() / 3600
    if total_hours > 12:
        text = f"‼️ Sleep duration is too long ({total_hours:.2f} hours). Please provide the correct wake-up time in 'HH:MM' format or type 'cancel' to discard this sleep record."
        await message.answer(
            translate_message(text, message.from_user.id),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(SleepCorrection.waiting_for_correct_time)
        await state.update_data(start_datetime=start_datetime)
        return

    hours = sleep_duration.seconds // 3600
    minutes = (sleep_duration.seconds // 60) % 60
    duration_str = f"{hours} H {minutes} Min"

    save_sleep_end(user_id, f"{current_date} {current_time}", duration_str)

    text = f"🥱 Sleep start:   {start_datetime.strftime('%H:%M    %Y-%m-%d')}\n⏰ Sleep end:     {end_datetime.strftime('%H:%M    %Y-%m-%d')}\n\n⏳ Sleep duration: {duration_str}\n"

    await message.answer(
        translate_message(text, message.from_user.id),
        reply_markup=create_dynamic_menu(user_id)
    )
    
    await message.answer(translate_message(f"💀🛏️ Sleep is over! {name}, did you sleep well?", message.from_user.id))
    await state.update_data(button_text="Mark the beginning of sleep")
    await message.answer(translate_message(f"💀 Mark the beginning of the sleep when you are ready to take a nap!", message.from_user.id), reply_markup=create_dynamic_menu(user_id))

@router.message(SleepCorrection.waiting_for_correct_time)
async def handle_correct_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text.strip()

    if user_input.lower() == "cancel":
        await message.answer(translate_message("❌ Sleep record discarded.", message.from_user.id), reply_markup=create_dynamic_menu(user_id))
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

        text = f"🥱 Sleep start:   {start_datetime.strftime('%H:%M    %Y-%m-%d')}\n⏰ Sleep end:     {end_datetime.strftime('%H:%M    %Y-%m-%d')}\n\n⏳ Sleep duration: {duration_str}\n"
        await message.answer(
            translate_message(text1, message.from_user.id),
            reply_markup=create_dynamic_menu(user_id)
        )
        await state.clear()
    except ValueError:
        await message.answer(translate_message("❗ Invalid time format. Please use 'HH:MM' or type 'cancel'.", message.from_user.id))

@router.message(F.text == "Show options")
async def show_options_handler(message: Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="option_1")],
        [InlineKeyboardButton(text="📜 Sleep History", callback_data="option_2")],
        [InlineKeyboardButton(text="💀 Start Chat", callback_data="start_chat")]
    ])
    await message.answer(translate_message("💀 Choose an option below:", message.from_user.id), reply_markup=inline_keyboard)

router.include_router(inline_router)
