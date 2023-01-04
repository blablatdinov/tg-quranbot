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
import uuid
from typing import Protocol

import nats
import pytz
from loguru import logger
from quranbot_schema_registry.validate_schema import validate_schema

from settings import settings


class SinkInterface(Protocol):
    """Интерфейс отправщика событий."""

    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """


class NatsSink(SinkInterface):
    """Отправщик событий в nats."""

    _queue_name = 'quranbot'

    async def send(self, event_data, event_name, version) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_version': version,
            'event_name': event_name,
            'event_time': str(datetime.datetime.now(pytz.timezone('Europe/Moscow'))),
            'producer': 'quranbot-aiogram',
            'data': event_data,
        }
        validate_schema(event, event_name, version)
        ns = await nats.connect(
            'nats://{0}:{1}'.format(settings.NATS_HOST, settings.NATS_PORT),
            token=settings.NATS_TOKEN,
        )
        jetstream = ns.jetstream()
        await jetstream.add_stream(name=self._queue_name)
        logger.info('Publishing to queue: {0}, event_id: {1}, event_name: {2}'.format(
            self._queue_name, event['event_id'], event['event_name'],
        ))
        await jetstream.publish(self._queue_name, json.dumps(event).encode('utf-8'))
        logger.info('Event: id={0} name={1} to queue: {2} successful published'.format(
            event['event_id'], event['event_name'], self._queue_name,
        ))
        await ns.close()
