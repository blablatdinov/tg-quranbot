import datetime

from aiogram import types

from db import DBConnection
from repository.prayer_time import PrayerTimeRepository
from repository.users.user import UserRepository
from services.prayer_time import PrayerTimes, UserPrayerStatus, UserPrayerTimes
from services.regular_expression import IntableRegularExpression
from utlls import get_bot_instance

bot = get_bot_instance()


async def mark_prayer_as_readed(callback_query: types.CallbackQuery):
    """Обработчик кнопки прочитанности аята.

    :param callback_query: app_types.CallbackQuery
    """
    async with DBConnection() as connection:
        user_prayer_status = UserPrayerStatus(
            prayer_times_repository=PrayerTimeRepository(connection),
            user_prayer_times=UserPrayerTimes(
                await PrayerTimes(
                    prayer_times_repository=PrayerTimeRepository(connection),
                    user_repository=UserRepository(connection),
                    chat_id=callback_query.from_user.id,
                ).get(),
                datetime.datetime.now(),
            ),
            user_prayer_id=IntableRegularExpression(r'\d+', callback_query.data),
        )

        await user_prayer_status.change(True)
        keyboard = await user_prayer_status.generate_refresh_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def mark_prayer_as_not_readed(callback_query: types.CallbackQuery):
    """Обработчик кнопки прочитанности аята.

    :param callback_query: app_types.CallbackQuery
    """
    async with DBConnection() as connection:
        user_prayer_status = UserPrayerStatus(
            prayer_times_repository=PrayerTimeRepository(connection),
            user_prayer_times=UserPrayerTimes(
                await PrayerTimes(
                    prayer_times_repository=PrayerTimeRepository(connection),
                    user_repository=UserRepository(connection),
                    chat_id=callback_query.from_user.id,
                ).get(),
                datetime.datetime.now(),
            ),
            user_prayer_id=IntableRegularExpression(r'\d+', callback_query.data),
        )

        await user_prayer_status.change(False)
        keyboard = await user_prayer_status.generate_refresh_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )
