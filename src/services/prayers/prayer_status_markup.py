from aiogram import types

from constants import PRAYER_READED_EMOJI, PRAYER_NOT_READED_EMOJI
from services.answers.answer import KeyboardInterface
from services.prayers.prayer_times import UserPrayerTimesInterface


class PrayerTimeKeyboard(KeyboardInterface):

    def __init__(self, user_prayer_times: UserPrayerTimesInterface):
        self._user_prayer_times = user_prayer_times

    async def generate(self):
        """Генерация.

        :returns: app_types.InlineKeyboardMarkup
        """
        keyboard = types.InlineKeyboardMarkup()
        user_prayers = await self._user_prayer_times.as_list()
        buttons = []
        for user_prayer in user_prayers:
            callback_data_template = 'mark_not_readed({0})' if user_prayer.is_readed else 'mark_readed({0})'
            buttons.append(types.InlineKeyboardButton(
                PRAYER_READED_EMOJI if user_prayer.is_readed else PRAYER_NOT_READED_EMOJI,
                callback_data=callback_data_template.format(user_prayer.id),
            ))

        keyboard.row(*buttons)

        return keyboard
