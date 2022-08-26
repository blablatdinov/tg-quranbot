import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import GET_PRAYER_TIMES_REGEXP
from db.connection import DBConnection, database
from repository.prayer_time import PrayerTimeRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from services.answers.answer import TextAnswer, DefaultKeyboard
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess
from services.prayer_time import PrayerTimes, UserHasNotCityExistsSafeAnswer, UserPrayerTimes, UserPrayerTimesAnswer, \
    UserPrayerTimesKeyboard
from utlls import BotInstance


async def prayer_times_handler(message: types.Message, state: FSMContext):
    """Получить времена намаза.

    :param message: types.Message
    :param state: FSMContext
    """
    user_prayer_times = UserPrayerTimes(
        PrayerTimes(
            PrayerTimeRepository(database),
            message.chat.id,
            UserRepository(database),
        ),
        datetime.datetime.now(),
    )
    await UserHasNotCityExistsSafeAnswer(
        UserPrayerTimesAnswer(
            BotInstance.get(),
            message.chat.id,
            user_prayer_times,
            datetime.datetime.now(),
            UserPrayerTimesKeyboard(user_prayer_times),
        ),
        TextAnswer(
            BotInstance.get(),
            message.chat.id,
            'asdf',
            DefaultKeyboard(),
        )
    ).send()
    await state.finish()


def register_prayer_times_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP), state='*')
