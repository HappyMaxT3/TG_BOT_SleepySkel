import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import router
from bot.storage import init_db, clean_old_sleep_data, get_all_user_ids
from bot.config import BOT_TOKEN
from bot.model_interaction import load_model_with_progress
from bot.commands import set_bot_commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def notify_startup(bot: Bot):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, "💀🦾 Wake the f*** up, samurai... We have the sleep to track!\nLet's go, darling! I'm working again.")
        except Exception as e:
            logger.warning(f"Failed to notify user {user_id}: {e}")

async def notify_shutdown(bot: Bot):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, "💀💤 See you soon, darling!\nI'm falling asleep too... It's time to rest...")
        except Exception as e:
            logger.warning(f"Failed to notify user {user_id}: {e}")

async def notify_updates(bot: Bot):
    user_ids = get_all_user_ids()
    update_message = "💀🚀 BIG UPDATE\n\nAdded Command Menu!"
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, update_message)
        except Exception as e:
            logger.warning(f"Failed to notify user {user_id} about updates: {e}")

def clear_sleep_history():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sleep_history")
        conn.commit()

def delete_reviews_by_user_ids(user_ids):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM reviews WHERE user_id = ?", [(user_id,) for user_id in user_ids])
        conn.commit()
        logger.info(f"Deleted reviews for user_ids: {user_ids}")

def delete_users_by_ids(user_ids):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM users WHERE user_id = ?", [(user_id,) for user_id in user_ids])
        cursor.executemany("DELETE FROM sleep_history WHERE user_id = ?", [(user_id,) for user_id in user_ids])
        cursor.executemany("DELETE FROM reviews WHERE user_id = ?", [(user_id,) for user_id in user_ids])
        conn.commit()
        logger.info(f"Deleted users and related data for user_ids: {user_ids}")

async def main():
    loop = asyncio.get_event_loop()
    model, tokenizer = await loop.run_in_executor(None, load_model_with_progress)

    session = AiohttpSession()
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp["model"] = model
    dp["tokenizer"] = tokenizer

    dp.include_router(router)

    await set_bot_commands(bot)

    init_db()
    clean_old_sleep_data()

    clear_history = input("❓ Clear sleep_history.db? (y - yes / `other_key` - skip): ").strip().lower()
    if clear_history in {"yes", "y", "Yes"}:
        clear_sleep_history()
    else:
        logger.info("⏩ Clearing sleep_history skipped.")

    action = input("🔧 Would you like to delete user data or reviews? (u - users/r - reviews/`other_key` - skip): ").strip().lower()
    if action in {"u", "r"}:
        user_ids_input = input("🆔 Enter user_ids to delete (comma or space separated): ").strip()
        user_ids = [int(uid) for uid in user_ids_input.replace(",", " ").split() if uid.isdigit()]
        if user_ids:
            if action == "u":
                delete_users_by_ids(user_ids)
            elif action == "r":
                delete_reviews_by_user_ids(user_ids)
        else:
            logger.warning("No valid user_ids entered. Skipping deletion.")
    else:
        logger.info("⏩ Deleting user data skipped.")

    notify_users = input("🔔 Notify users about bot startup? (y - yes/`other_key` - skip): ").strip().lower()
    if notify_users in {"yes", "y", "Y"}:
        logger.info("Notifying users about startup...")
        await notify_startup(bot)
    else:
        logger.info("⏩ Startup notification skipped.")

    notify_update = input("🚀 Notify users about updates? (y - yes/`other_key` - skip): ").strip().lower()
    if notify_update in {"yes", "y", "Y"}:
        logger.info("Notifying users about updates...")
        await notify_updates(bot)
    else:
        logger.info("⏩ Update notification skipped.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if notify_users in {"yes", "y", "Y"}:
            logger.info("Notifying users about shutdown...")
            await notify_shutdown(bot)
        await bot.session.close()
        logger.info("Bot session closed.")

if __name__ == "__main__":
    asyncio.run(main())
