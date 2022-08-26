import datetime

from aiogram import types

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.prayer_time import PrayerTimeRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from services.answers.log_answer import LoggedSourceCallback
from services.ayats.edit_markup import Markup
from services.prayers.prayer_status import PrayerStatus
from services.prayers.prayer_status_markup import PrayerTimeKeyboard
from services.prayers.prayer_times import EditedUserPrayerTimes, PrayersWithoutSunrise, PrayerTimes, UserPrayerTimes
from utlls import BotInstance, get_bot_instance

bot = get_bot_instance()


async def change_prayer_status(callback_query: types.CallbackQuery):
    """Обработчик кнопки прочитанности аята.

    :param callback_query: app_types.CallbackQuery
    """
    await LoggedSourceCallback(
        Markup(
            BotInstance.get(),
            callback_query.from_user.id,
            callback_query.message.message_id,
            PrayerTimeKeyboard(
                EditedUserPrayerTimes(
                    UserPrayerTimes(
                        callback_query.from_user.id,
                        PrayersWithoutSunrise(
                            PrayerTimes(
                                callback_query.from_user.id,
                                UserRepository(database),
                                PrayerTimeRepository(database),
                                datetime.datetime.today(),
                            ),
                        ),
                        UserRepository(database),
                        PrayerTimeRepository(database),
                    ),
                    PrayerTimeRepository(database),
                    PrayerStatus(callback_query.data),
                ),
            ),
        ),
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        callback_query,
    ).edit()
