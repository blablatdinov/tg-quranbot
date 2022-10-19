import datetime
import json
import uuid
from typing import Protocol

import nats
from loguru import logger
from quranbot_schema_registry.validate_schema import validate_schema


class SinkInterface(Protocol):
    """Интерфейс отправщика событий."""

    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


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
            'event_time': str(datetime.datetime.now()),
            'producer': 'quranbot-aiogram',
            'data': event_data,
        }
        ns = await nats.connect('localhost:4222')
        validate_schema(event, event_name, version)
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
