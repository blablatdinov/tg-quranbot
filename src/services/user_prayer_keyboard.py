import datetime
import json

from constants import PrayerNotReadedEmoji, PrayerReadedEmoji
from integrations.tg.tg_answers.update import Update
from repository.prayer_time import UserPrayersInterface
from services.answers.answer import KeyboardInterface
from services.user_prayer_button_callback import UserPrayersButtonCallback


class UserPrayersKeyboard(KeyboardInterface):
    """Клавиатура времен намаза."""

    def __init__(self, user_prayer_times: UserPrayersInterface, date: datetime.date):
        self._user_prayer_times = user_prayer_times
        self._date = date

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return json.dumps({
            'inline_keyboard': [[
                {
                    'text': str(PrayerReadedEmoji()) if user_prayer.is_readed else str(PrayerNotReadedEmoji()),
                    'callback_data': str(UserPrayersButtonCallback(user_prayer)),
                }
                for user_prayer in await self._user_prayer_times.prayer_times(update.chat_id(), self._date)
            ]],
        })
