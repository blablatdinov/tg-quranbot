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
import asyncio
import json
from typing import Protocol, final, override

import aio_pika
import attrs
from databases import Database
from eljson.json_doc import JsonDoc
from loguru import logger
from pyeo import elegant
from quranbot_schema_registry import validate_schema

from app_types.runable import SyncRunable
from settings.settings import Settings
from srv.events.recieved_event import ReceivedEvent


@elegant
class EventHook(Protocol):
    """Обработчик событий из очереди."""

    async def catch(self) -> None:
        """Запуск обработки."""


@final
@attrs.define(frozen=True)
@elegant
class EventHookApp(SyncRunable):
    """Запускаемый объект."""

    _event_hook: EventHook

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        asyncio.run(self._event_hook.catch())
        return 0


@final
@attrs.define(frozen=True)
@elegant
class RbmqEventHook(EventHook):
    """Обработчик событий из RabbitMQ."""

    _settings: Settings
    _pgsql: Database
    _event: ReceivedEvent

    @override
    async def catch(self) -> None:  # noqa: WPS217
        """Запуск обработки."""
        await self._pgsql.connect()
        connection = await aio_pika.connect_robust(
            'amqp://{0}:{1}@{2}:5672/default_vhost'.format(
                self._settings.RABBITMQ_USER,
                self._settings.RABBITMQ_PASS,
                self._settings.RABBITMQ_HOST,
            ),
        )
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.declare_queue('quranbot_queue')
            async with queue.iterator() as queue_iter:
                await self._iter_messages(queue_iter)

    async def _iter_messages(self, queue_iter: aio_pika.abc.AbstractQueueIterator) -> None:
        async for message in queue_iter:
            async with message.process():
                await self._callback(message)

    async def _callback(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        decoded_body = message.body.decode('utf-8')
        logger.info('Taked event {0}'.format(decoded_body))
        body_json = JsonDoc.from_string(decoded_body)  # type: ignore [no-untyped-call]
        try:
            validate_schema(
                json.loads(decoded_body),
                body_json.path('$.event_name')[0],
                body_json.path('$.event_version')[0],
            )
        except TypeError as err:
            logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json.path('$.event_id')[0], str(err),
            ))
            return
        await self._event.process(body_json)
