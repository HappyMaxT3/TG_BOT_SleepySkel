from aiogram import Bot
from aiogram.types import BotCommand

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="🏁💀 Start SleepySkel"),
        BotCommand(command="/info", description="ℹ️🗝️ Instructions and Capabilities"),
        BotCommand(command="/set_language", description="🌐💀 Choose Bot language"),
    ]
    await bot.set_my_commands(commands)
