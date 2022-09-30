import datetime

import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from repository.prayer_time import PrayersWithoutSunrise
from repository.user_prayers_interface import UserPrayersInterface
from services.prayers.prayer_status import PrayerStatus, UserPrayerStatusInterface
from services.user_prayer_keyboard import UserPrayersKeyboard


class UserPrayerStatusChangeAnswer(TgAnswerInterface):
    """Ответ с изменением статуса прочитанности намаза."""

    def __init__(
        self,
        answer: TgAnswerInterface,
        prayer_status: UserPrayerStatusInterface,
        user_prayers: UserPrayersInterface,
    ):
        self._origin = answer
        self._prayer_status = prayer_status
        self._user_prayers = user_prayers

    async def build(self, update) -> list[httpx.Request]:
        """Обработка запроса.

        :param update: Update
        :return: list[httpx.Request]
        """
        await self._prayer_status.change(PrayerStatus(update.callback_query().data))
        return await TgAnswerMarkup(
            TgMessageIdAnswer(
                self._origin,
                update.callback_query().message.message_id,
            ),
            UserPrayersKeyboard(PrayersWithoutSunrise(self._user_prayers), datetime.date.today()),
        ).build(update)
