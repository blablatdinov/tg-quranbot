import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import GET_PRAYER_TIMES_REGEXP
from db import DBConnection
from repository.prayer_time import PrayerTimeRepository
from repository.users.user import UserRepository
from services.prayer_time import PrayerTimes, UserHasNotCityExistsSafeAnswer, UserPrayerTimes, UserPrayerTimesAnswer


async def prayer_times_handler(message: types.Message, state: FSMContext):
    """Получить времена намаза.

    :param message: types.Message
    :param state: FSMContext
    """
    async with DBConnection() as connection:
        answer = await UserHasNotCityExistsSafeAnswer(
            UserPrayerTimesAnswer(
                UserPrayerTimes(
                    PrayerTimes(
                        prayer_times_repository=PrayerTimeRepository(connection),
                        user_repository=UserRepository(connection),
                        chat_id=message.chat.id,
                    ),
                    datetime.datetime.now(),
                ),
            ),
        ).to_answer()

    await state.finish()
    await answer.send(message.chat.id)


def register_prayer_times_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP), state='*')
