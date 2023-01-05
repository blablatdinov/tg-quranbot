"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
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
        """Конструктор класса.

        :param user_prayer_times: UserPrayersInterface
        :param date: datetime.date
        :param chat_id: int
        """
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
        """Конструктор класса.

        :param user_prayer_times: UserPrayersInterface
        :param date: datetime.date
        """
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
