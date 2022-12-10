import datetime
import json

from app_types.stringable import Stringable
from constants import PrayerNotReadedEmoji, PrayerReadedEmoji
from integrations.tg.chat_id import TgChatId
from repository.user_prayers_interface import UserPrayersInterface
from services.answers.answer import KeyboardInterface
from services.user_prayer_button_callback import UserPrayersButtonCallback


class UserPrayersKeyboardByChatId(KeyboardInterface):
    """Клавиатура времен намаза с идентификатором чата в конструкторе."""

    def __init__(self, user_prayer_times: UserPrayersInterface, date: datetime.date, chat_id: int):
        self._user_prayer_times = user_prayer_times
        self._date = date
        self._chat_id = chat_id

    async def generate(self, update: Stringable) -> str:
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return json.dumps({
            'inline_keyboard': [[
                {
                    'text': str(PrayerReadedEmoji()) if user_prayer.is_readed else str(PrayerNotReadedEmoji()),
                    'callback_data': str(UserPrayersButtonCallback(user_prayer)),
                }
                for user_prayer in await self._user_prayer_times.prayer_times(self._chat_id, self._date)
            ]],
        })


class UserPrayersKeyboard(KeyboardInterface):
    """Клавиатура времен намаза."""

    def __init__(self, user_prayer_times: UserPrayersInterface, date: datetime.date):
        self._user_prayer_times = user_prayer_times
        self._date = date

    async def generate(self, update: Stringable) -> str:
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return await UserPrayersKeyboardByChatId(
            self._user_prayer_times,
            self._date,
            int(TgChatId(update)),
        ).generate(update)
