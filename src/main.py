import asyncpg
from aiogram import Bot, Dispatcher, executor, types

from settings import settings

bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Ответ на команды: start, help.

    :param message: types.Message
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(commands=['ping_db'])
async def ping_db(message: types.Message):
    """Проверка подключения к БД.

    :param message: types.Message
    """
    conn = await asyncpg.connect(settings.DATABASE_URL)
    row = await conn.fetchrow('select 1')
    await conn.close()
    await message.answer(row)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
