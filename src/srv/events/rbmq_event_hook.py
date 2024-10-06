# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import asyncio
from collections.abc import Iterable
from typing import final, override

import aio_pika
import attrs
import ujson
from aiormq.abc import DeliveredMessage
from databases import Database
from eljson.json_doc import JsonDoc
from quranbot_schema_registry import validate_schema

from app_types.logger import LogSink
from settings import Settings
from srv.events.event_hook import EventHook
from srv.events.recieved_event import ReceivedEvent


@final
@attrs.define(frozen=True)
class RbmqEventHook(EventHook):
    """Обработчик событий из RabbitMQ."""

    _settings: Settings
    _pgsql: Database
    _logger: LogSink
    _events: Iterable[ReceivedEvent]

    @classmethod
    def ctor(
        cls,
        settings: Settings,
        pgsql: Database,
        logger: LogSink,
        *events: ReceivedEvent,
    ) -> EventHook:
        """Ctor.

        :param settings: Settings,
        :param pgsql: Database,
        :param logger: LogSink,
        :param events: ReceivedEvent,
        :return: EventHook
        """
        return cls(
            settings,
            pgsql,
            logger,
            events,
        )

    @override
    async def catch(self) -> None:  # noqa: WPS217
        """Запуск обработки."""
        await self._pgsql.connect()
        connection = await aio_pika.connect_robust(
            'amqp://{0}:{1}@{2}:5672/{3}'.format(
                self._settings.RABBITMQ_USER,
                self._settings.RABBITMQ_PASS,
                self._settings.RABBITMQ_HOST,
                self._settings.RABBITMQ_VHOST,
            ),
        )
        self._logger.info('Connected to rabbitmq')
        async with connection:
            chnl = await connection.channel()
            channel = await chnl.get_underlay_channel()
            self._logger.info('Wait events...')
            while True:  # noqa: WPS457
                await asyncio.sleep(0.1)
                for queue_name in ('quranbot.users', 'quranbot.mailings', 'quranbot.ayats', 'quranbot.messages'):
                    msg: DeliveredMessage = await channel.basic_get(queue_name)
                    await self._event_handler(msg, chnl)

    async def _event_handler(self, message: DeliveredMessage, chnl: aio_pika.abc.AbstractChannel) -> None:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_event_handler"
        if not message.body:
            return
        try:
            await self._inner_handler(message)
        except Exception:  # pylint: disable=broad-exception-caught
            # Catching all exceptions because app entry.
            self._logger.exception('Fail on process event')
            await chnl.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key='failed-events',
            )
        await message.channel.basic_ack(message.delivery.delivery_tag)  # type: ignore [union-attr, arg-type]

    async def _inner_handler(self, message: DeliveredMessage) -> None:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_inner_handler"
        decoded_body = message.body.decode('utf-8')
        self._logger.info('Taked event {0}'.format(decoded_body))
        body_json = JsonDoc.from_string(decoded_body)  # type: ignore [no-untyped-call]
        try:
            validate_schema(
                ujson.loads(decoded_body),
                body_json.path('$.event_name')[0],
                body_json.path('$.event_version')[0],
            )
        except TypeError as err:
            self._logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json.path('$.event_id')[0], str(err),
            ))
            return
        for event in self._events:
            await event.process(body_json)
        self._logger.info('Event {0} processed'.format(body_json.path('$.event_id')[0]))
