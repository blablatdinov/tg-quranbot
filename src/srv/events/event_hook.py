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
import asyncio
import json
from typing import Protocol, final

import aioamqp
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

    async def catch(self) -> None:
        """Запуск обработки."""
        channel, transport, protocol = await self._pre_build()
        await channel.basic_consume(self._callback, queue_name='my_queue')
        try:  # noqa: WPS501
            while True:  # noqa: WPS457
                await asyncio.sleep(1)
        finally:
            await protocol.close()
            transport.close()

    async def _pre_build(self) -> tuple:
        await self._pgsql.connect()
        transport, protocol = await aioamqp.connect(
            host=self._settings.RABBITMQ_HOST,
            login=self._settings.RABBITMQ_USER,
            password=self._settings.RABBITMQ_PASS,
        )
        channel = await protocol.channel()
        await channel.queue_declare(queue_name='my_queue')
        return channel, transport, protocol

    async def _callback(
        self,
        channel: aioamqp.channel.Channel,
        body: bytes,
        envelope: aioamqp.envelope.Envelope,
        properties: aioamqp.properties.Properties,
    ) -> None:
        logger.info('Taked event {0}'.format(json.loads(body.decode('utf-8'))))
        body_json = JsonDoc.from_string(body.decode('utf-8'))  # type: ignore [no-untyped-call]
        try:
            validate_schema(
                json.loads(body.decode('utf-8')),
                body_json.path('$.event_name')[0],
                body_json.path('$.event_version')[0],
            )
        except TypeError as err:
            logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json.path('$.event_id')[0], str(err),
            ))
            return
        await self._event.process(body_json)
        await channel.basic_client_ack(envelope.delivery_tag)
