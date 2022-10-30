import asyncio
import datetime
import json
from typing import Protocol

import nats
from databases import Database
from loguru import logger
from quranbot_schema_registry import validate_schema

from app_types.runable import Runable
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


class RecievedEvents(Runable):
    """Обработка событий из очереди."""

    _queue_name = 'quranbot'

    def __init__(self, *events: RecievedEventInterface):
        self._handlers = events

    async def run(self):
        """Запуск."""
        nats_client = await nats.connect('localhost')
        logger.info('Start handling events...')
        logger.info('Receive evenst list: {0}'.format([event_handler.name for event_handler in self._handlers]))
        await nats_client.subscribe(self._queue_name, cb=self._message_handler)
        while True:  # noqa: WPS457
            await asyncio.sleep(0.1)

    async def _message_handler(self, event):
        event_dict = json.loads(event.data.decode())
        event_log_data = 'event_id={0} event_name={1} event_version={2}'.format(
            event_dict['event_name'],
            event_dict['event_id'],
            event_dict['event_version'],
        )
        logger.info('Event {0} received'.format(event_log_data))
        try:
            validate_schema(event_dict, event_dict['event_name'], event_dict['event_version'])
        except TypeError as event_validate_error:
            logger.error('Validate {0} failed {1}'.format(event_log_data, str(event_validate_error)))
            return
        for event_handler in self._handlers:
            if event_handler.name == event_dict['event_name'] and event_dict['event_version'] == event_handler.version:
                logger.info('Handling {0} event...'.format(event_log_data))
                await event_handler.handle_event(event_dict['data'])
                logger.info('Event {0} handled successful'.format(event_log_data))
                return
        logger.info('Event {0} skipped'.format(event_log_data))
