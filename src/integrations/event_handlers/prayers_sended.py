import datetime
from typing import Protocol

from databases import Database

from integrations.tg.sendable import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgChatIdAnswer, TgMessageAnswer, TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.prayer_time import (
    NewUserPrayers,
    PrayersWithoutSunrise,
    SafeNotFoundPrayers,
    SafeUserPrayers,
    UserPrayers,
)
from repository.users.users import UsersRepositoryInterface
from services.user_prayer_keyboard import UserPrayersKeyboardByChatId


class RecievedEventInterface(Protocol):
    """Интерфейс обрабатываемых событий."""

    name: str
    version: int

    async def handle_event(self, event_data: dict) -> None:
        """Обработка события.

        :param event_data: dict
        """


class SendPrayersEvent(RecievedEventInterface):
    """Событие о рассылки времени намаза."""

    name = 'Prayers.Sended'
    version = 1

    _time_format = '%H:%M'
    _template = '\n'.join([
        'Время намаза для г. {city_name} ({date})\n',
        'Иртәнге: {fajr_prayer_time}',
        'Восход: {sunrise_prayer_time}',
        'Өйлә: {dhuhr_prayer_time}',
        'Икенде: {asr_prayer_time}',
        'Ахшам: {magrib_prayer_time}',
        'Ястү: {ishaa_prayer_time}',
    ])

    def __init__(self, users_repo: UsersRepositoryInterface, empty_answer: TgAnswerInterface, database: Database):
        """Конструктор класса.

        :param users_repo: UsersRepositoryInterface
        :param empty_answer: TgAnswerInterface
        :param database: Database
        """
        self._users_repo = users_repo
        self._empty_answer = empty_answer
        self._database = database

    async def handle_event(self, event_data: dict):
        """Обработать событие.

        :param event_data: dict
        """
        deactivated_users = []
        chat_ids = await self._users_repo.active_users_with_city()
        answers = await self._build_requests(chat_ids)
        for response_list in await BulkSendableAnswer(answers).send(Update(update_id=0).json()):
            for response_dict in response_list:
                if not response_dict['ok']:
                    deactivated_users.append(response_dict['chat_id'])
        await self._users_repo.update_status(list(set(deactivated_users)), to=False)

    async def _build_requests(self, chat_ids: list[int]) -> list[TgAnswerInterface]:
        answers: list[TgAnswerInterface] = []
        target_date = datetime.datetime.now() + datetime.timedelta(days=1)
        for chat_id in chat_ids:
            safe_not_found_prayers = SafeNotFoundPrayers(
                self._database,
                SafeUserPrayers(
                    UserPrayers(self._database),
                    NewUserPrayers(
                        self._database,
                        UserPrayers(self._database),
                    ),
                ),
            )
            prayers = await safe_not_found_prayers.prayer_times(chat_id, target_date)
            answers.append(
                TgAnswerMarkup(
                    TgTextAnswer(
                        TgChatIdAnswer(
                            TgMessageAnswer(self._empty_answer),
                            chat_id,
                        ),
                        self._template.format(
                            city_name=prayers[0].city,
                            date=prayers[0].day.strftime('%d.%m.%Y'),
                            fajr_prayer_time=prayers[0].time.strftime(self._time_format),
                            sunrise_prayer_time=prayers[1].time.strftime(self._time_format),
                            dhuhr_prayer_time=prayers[2].time.strftime(self._time_format),
                            asr_prayer_time=prayers[3].time.strftime(self._time_format),
                            magrib_prayer_time=prayers[4].time.strftime(self._time_format),
                            ishaa_prayer_time=prayers[5].time.strftime(self._time_format),
                        ),
                    ),
                    UserPrayersKeyboardByChatId(
                        PrayersWithoutSunrise(safe_not_found_prayers),
                        target_date,
                        chat_id,
                    ),
                ),
            )
        return answers
