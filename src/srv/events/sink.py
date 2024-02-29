"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import json
from typing import Protocol, final, override

import aio_pika
import attrs
from loguru import logger
from pyeo import elegant
from quranbot_schema_registry import validate_schema

from settings.settings import Settings


@elegant
class SinkInterface(Protocol):
    """Интерфейс отправщика событий."""

    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """


@final
@attrs.define(frozen=True)
@elegant
class FkSink(SinkInterface):
    """Фейковый слив для событий."""

    @override
    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """


@final
@attrs.define(frozen=True)
@elegant
class RabbitmqSink(SinkInterface):

    _settings: Settings

    @override
    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """
        body_json = json.dumps(event_data)
        try:
            validate_schema(
                body_json,
                event_name,
                version,
            )
        except TypeError as err:
            logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json.path('$.event_id')[0], str(err),
            ))
            return
        connection = await aio_pika.connect_robust(
            'amqp://{0}:{1}@{2}:5672/{3}'.format(
                self._settings.RABBITMQ_USER,
                self._settings.RABBITMQ_PASS,
                self._settings.RABBITMQ_HOST,
                self._settings.RABBITMQ_VHOST,
            ),
        )
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=body_json.encode('utf-8')),
                routing_key="quranbot_queue",
            )
