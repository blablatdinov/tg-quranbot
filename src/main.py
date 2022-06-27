import asyncpg
from aiogram import Bot, Dispatcher, executor, types

from settings import settings
from services.register_user import RegisterUser
from services.ayat import AyatsService
from repository.ayats import AyatRepository
from repository.admin_message import AdminMessageRepository
from repository.user import UserRepository

bot = Bot(token=settings.API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    try:
        connection = await asyncpg.connect(settings.DATABASE_URL)
        answers = await RegisterUser(
            user_repository=UserRepository(connection),
            admin_messages_repository=AdminMessageRepository(connection),
            ayat_service=AyatsService(
                AyatRepository(connection),
            ),
            chat_id=message.chat.id,
        ).register()
        for answer in answers:
            await message.answer(answer)
    except Exception as e:
        await message.reply(f"Exception: {e}")
        raise e
    finally:
        await connection.close()


@dp.message_handler(commands=['ping_db'])
async def ping_db(message: types.Message):
    """Проверка подключения к БД.

    :param message: types.Message
    """
    try:
        connection = await asyncpg.connect(settings.DATABASE_URL)
        ayat = await AyatsService(
            AyatRepository(connection),
        ).get_formatted_first_ayat()
        return await message.answer(ayat)
    finally:
        await connection.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
