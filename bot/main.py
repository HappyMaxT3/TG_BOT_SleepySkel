import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import router
from bot.storage import init_db, clean_old_sleep_data, get_all_user_ids
from bot.config import BOT_TOKEN
from bot.model_interaction import load_model_with_progress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def notify_startup(bot: Bot):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, "💀🦾 Wake the f*** up, samurai... We have the sleep to track!\nLet`s go, darling! I`m workind again.")
        except Exception as e:
            logger.warning(f"Failed to notify user {user_id}: {e}")

async def notify_shutdown(bot: Bot):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, "💀💤 See you soon, darling!\nI`m falling asleep too... It`s time to rest...")
        except Exception as e:
            logger.warning(f"Failed to notify user {user_id}: {e}")

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

    init_db()
    clean_old_sleep_data()

    notify_users = input("🔔 Notify users about bot startup? (yes/no): ").strip().lower()
    if notify_users in {"yes", "y"}:
        logger.info("Notifying users about startup...")
        await notify_startup(bot)
    else:
        logger.info("Startup notification skipped.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if notify_users in {"yes", "y"}:
            logger.info("Notifying users about shutdown...")
            await notify_shutdown(bot)
        await bot.session.close()
        logger.info("Bot session closed.")

if __name__ == "__main__":
    asyncio.run(main())
