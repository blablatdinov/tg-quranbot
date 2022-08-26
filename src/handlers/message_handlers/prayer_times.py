import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import GET_PRAYER_TIMES_REGEXP
from db.connection import database
from repository.prayer_time import PrayerTimeRepository
from repository.users.user import UserRepository
from services.prayers.prayer_status_markup import PrayerTimeKeyboard
from services.prayers.prayer_times import PrayerTimes, PrayerForUserAnswer, UserPrayerTimes
from utlls import BotInstance


async def prayer_times_handler(message: types.Message, state: FSMContext):
    """Получить времена намаза.

    :param message: types.Message
    :param state: FSMContext
    """
    await PrayerForUserAnswer(
        BotInstance.get(),
        message.chat.id,
        PrayerTimes(
            message.chat.id,
            UserRepository(database),
            PrayerTimeRepository(database),
            datetime.datetime.today(),
        ),
        PrayerTimeKeyboard(
            UserPrayerTimes(
                message.chat.id,
                PrayerTimes(
                    message.chat.id,
                    UserRepository(database),
                    PrayerTimeRepository(database),
                    datetime.datetime.today(),
                ),
                UserRepository(database),
                PrayerTimeRepository(database),
            ),
        ),
    ).send()
    await state.finish()


def register_prayer_times_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP), state='*')
