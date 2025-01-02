from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.storage import (
    get_average_sleep_duration_last_7_days,
    get_total_sleep_duration_last_7_days,
    get_anonymous_average_sleep
)

router = Router()

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
    await callback.message.answer(response)
    await callback.answer()

@router.callback_query(F.data == "option_2")
async def option_2_handler(callback: CallbackQuery):
    await callback.message.answer("🟡 You chose Option 2!")
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):
    await callback.message.answer("❌ Action cancelled.")
    await callback.answer()
