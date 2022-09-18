import asyncio

from loguru import logger

from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable import SendableInterface


class PollingApp(object):
    """Приложение на long polling."""

    def __init__(self, updates: PollingUpdatesIterator, sendable: SendableInterface):
        self._sendable = sendable
        self._updates = updates

    async def run(self):
        """Запуск."""
        logger.info('Start app on polling')
        async for update_list in self._updates:
            for update in update_list:
                await self._sendable.send(update)
                await asyncio.sleep(0.1)
