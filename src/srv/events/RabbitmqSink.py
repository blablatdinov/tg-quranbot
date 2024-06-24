import time
import uuid
from typing import final, override

import aio_pika
import attrs
import ujson
from loguru import logger
from pyeo import elegant
from quranbot_schema_registry import validate_schema

from app_types.logger import LogSink
from settings import Settings
from srv.events.sink import Sink


@final
@attrs.define(frozen=True)
@elegant
class RabbitmqSink(Sink):
    """События в rabbitmq."""

    _settings: Settings
    _logger: LogSink

    @override
    async def send(self, queue_name: str, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param queue_name: str
        :param event_data: dict
        :param event_name: str
        :param version: int
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_version': 1,
            'event_name': event_name,
            'event_time': str(int(time.time())),
            'producer': 'quranbot',
            'data': event_data,
        }
        body_json = ujson.dumps(event)
        try:
            validate_schema(
                body_json,
                event_name,
                version,
            )
        except TypeError as err:
            logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json, str(err),
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
        self._logger.info('Try to publish event: {0}'.format(body_json))
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=body_json.encode('utf-8')),
                routing_key=queue_name,
            )
        self._logger.info('Event: {0} published'.format(body_json))
