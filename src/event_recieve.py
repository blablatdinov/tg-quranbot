import asyncio
import json

import nats
from loguru import logger
from quranbot_schema_registry import validate_schema

from app_types.runable import Runable
from integrations.event_handlers.prayers_sended import RecievedEventInterface


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
