import datetime

import httpx

from integrations.tg.tg_answers import TgTextAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from repository.prayer_time import PrayersWithoutSunrise
from repository.user_prayers_interface import UserPrayersInterface
from services.prayers.prayer_status import PrayerStatus, UserPrayerStatusInterface
from services.user_prayer_keyboard import UserPrayersKeyboard


class PrayerForUserAnswer(TgAnswerInterface):
    """Ответ пользователю с временами намаза."""

    def __init__(
        self,
        answer: TgAnswerInterface,
        user_prayers: UserPrayersInterface,
    ):
        self._origin = answer
        self._user_prayers = user_prayers

    async def build(self, update) -> list[httpx.Request]:
        """Отправить.

        :param update: Stringable
        :return: list[types.Message]
        """
        prayers = await self._user_prayers.prayer_times(
            update.chat_id(), datetime.date.today(),
        )
        time_format = '%H:%M'
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        return await TgAnswerMarkup(
            TgTextAnswer(
                self._origin,
                template.format(
                    city_name=prayers[0].city,
                    date=prayers[0].day.strftime('%d.%m.%Y'),
                    fajr_prayer_time=prayers[0].time.strftime(time_format),
                    sunrise_prayer_time=prayers[1].time.strftime(time_format),
                    dhuhr_prayer_time=prayers[2].time.strftime(time_format),
                    asr_prayer_time=prayers[3].time.strftime(time_format),
                    magrib_prayer_time=prayers[4].time.strftime(time_format),
                    ishaa_prayer_time=prayers[5].time.strftime(time_format),
                ),
            ),
            UserPrayersKeyboard(PrayersWithoutSunrise(self._user_prayers), datetime.date.today()),
        ).build(update)


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

        :param update: Stringable
        :return: list[httpx.Request]
        """
        await self._prayer_status.change(PrayerStatus(update.callback_query().data))
        return await TgAnswerMarkup(
            TgMessageIdAnswer(
                self._origin,
                update.message_id(),
            ),
            UserPrayersKeyboard(PrayersWithoutSunrise(self._user_prayers), datetime.date.today()),
        ).build(update)
