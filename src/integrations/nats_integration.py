import asyncio
import datetime
import json
import uuid

import nats
from loguru import logger
from quranbot_schema_registry.validate_schema import validate_schema


class MessageBrokerInterface(object):
    """Интерфейс брокера сообщений."""

    async def receive(self):
        """Обработка сообщений из очереди.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def send(self, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class NatsIntegration(MessageBrokerInterface):
    """Интеграция с nats."""

    _queue_name = 'default'

    def __init__(self, handlers: list):
        self._handlers = handlers

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
        validate_schema(event, event_name, version)
        nats_client = await nats.connect('localhost')
        jetstream = nats_client.jetstream()

        logger.info('Publishing to queue: {0}, event_id: {1}, event_name: {2}'.format(
            self._queue_name, event['event_id'], event['event_name'],
        ))
        await jetstream.publish(self._queue_name, json.dumps(event).encode('utf-8'))
        logger.info('Event: id={0} name={1} to queue: {2} successful published'.format(
            event['event_id'], event['event_name'], self._queue_name,
        ))
        await nats_client.close()

    async def receive(self) -> None:
        """Прием сообщений."""
        nats_client = await nats.connect('localhost')
        logger.info('Start handling events...')
        logger.info('Receive evenst list: {0}'.format([event_handler.event_name for event_handler in self._handlers]))
        js = nats_client.jetstream()
        await js.subscribe('default', durable='quranbot_aiogram', cb=self._message_handler)
        while True:  # noqa: WPS457
            await asyncio.sleep(1)

    async def _message_handler(self, event):
        event_dict = json.loads(event.data.decode())
        event_log_data = 'event_id={0} event_name={1}'.format(event_dict['event_name'], event_dict['event_id'])
        logger.info('Event {0} received'.format(event_log_data))
        try:
            validate_schema(event_dict, event_dict['event_name'], event_dict['event_version'])
        except TypeError as event_validate_error:
            logger.error('Validate {0} failed {1}'.format(event_log_data, str(event_validate_error)))
            return

        for event_handler in self._handlers:
            if event_handler.event_name == event_dict['event_name']:
                logger.info('Handling {0} event...'.format(event_log_data))
                await event_handler.handle_event(event_dict['data'])
                logger.info('Event {0} handled successful'.format(event_log_data))
                return

        logger.info('Event {0} skipped'.format(event_log_data))
