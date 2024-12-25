from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "option_1")
async def option_1_handler(callback: CallbackQuery):
    await callback.message.answer("🟢 You chose Option 1!")
    await callback.answer()

@router.callback_query(F.data == "option_2")
async def option_2_handler(callback: CallbackQuery):
    await callback.message.answer("🟡 You chose Option 2!")
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):
    await callback.message.answer("❌ Action cancelled.")
    await callback.answer()
