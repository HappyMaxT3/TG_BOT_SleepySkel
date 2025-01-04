from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from bot.storage import (
    get_average_sleep_duration_last_7_days,
    get_total_sleep_duration_last_7_days,
    get_anonymous_average_sleep,
    get_sleep_history_last_7_days,
    add_feedback
)
from bot.model_interaction import get_model_response
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigscience/bloomz-1b1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

router = Router()
user_chat_state = {}

@router.callback_query(F.data == "option_1")
async def sleep_stats_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    avg_sleep = get_average_sleep_duration_last_7_days(user_id)
    total_sleep = get_total_sleep_duration_last_7_days(user_id)
    anon_avg_sleep = get_anonymous_average_sleep()

    response = (
        f"📊 Your sleep statistics for the last 7 days:\n"
        f"• Average sleep duration: {avg_sleep} min\n"
        f"• Total sleep duration: {total_sleep} min\n\n"
        f"📈 Statistics of all users:\n"
        f"• Average sleep duration: {anon_avg_sleep} min"
    )
    await callback.message.edit_text(response)
    await callback.answer()

@router.callback_query(F.data == "option_2")
async def option_2_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    sleep_history = get_sleep_history_last_7_days(user_id)

    if not sleep_history:
        response = "💀 You have no sleep records for the last 7 days."
    else:
        response = "💀📜 Your sleep history for the last 7 days:\n\n"
        for sleep_start, sleep_end, sleep_duration in sleep_history:
            response += f"🕝 {sleep_start} - {sleep_end}\n      {sleep_duration}\n\n"

    await callback.message.edit_text(response)
    await callback.answer()

@router.callback_query(F.data == "start_chat")
async def start_chat_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer("💀💤 Hello! I am SleepySkel. We can talk about your dreams or smth. Type 'stop' to end the conversation.")
    await callback.answer()
    user_chat_state[user_id] = True

@router.message(F.text == "stop")
async def stop_chat_handler(message: Message):
    user_id = message.from_user.id
    if user_chat_state.get(user_id):
        user_chat_state[user_id] = False
        await message.answer("💀🔚 Chat with SleepySkel has ended.")
    else:
        await message.answer("💀❌ You are not in a chat.")

@router.message()
async def chat_with_model_handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if 'feedback' in text:
        review_text = text.replace('feedback', '').strip()
        add_feedback(user_id, review_text)
        await message.answer("💀 Thank you for your feedback! It has been saved.")
        return

    if user_chat_state.get(user_id):
        if text == "stop":
            await stop_chat_handler(message)
        else:
            model_response = get_model_response(model, tokenizer, text, user_id)
            await message.answer(model_response)
    else:
        await message.answer("💀🔒 You are not in a chat with SleepySkel. Choose an option to begin!")
