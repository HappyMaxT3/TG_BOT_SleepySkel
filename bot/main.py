import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import router
from bot.storage import init_db, clean_old_sleep_data
from bot.config import BOT_TOKEN
from bot.model_interaction import load_model_with_progress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Загрузка модели и токенизатора
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

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
