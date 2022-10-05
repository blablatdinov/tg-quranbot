import asyncio

from databases import Database
from loguru import logger

from app_types.runable import Runable
from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable import SendableInterface


class PollingApp(Runable):
    """Приложение на long polling."""

    def __init__(self, updates: PollingUpdatesIterator, sendable: SendableInterface):
        self._sendable = sendable
        self._updates = updates

    async def run(self) -> None:
        """Запуск."""
        logger.info('Start app on polling')
        async for update_list in self._updates:
            for update in update_list:
                asyncio.ensure_future(self._sendable.send(update))
                await asyncio.sleep(0.1)


class DatabaseConnectedApp(Runable):
    """Декоратор для подключения к БД."""

    def __init__(self, database: Database, app: Runable) -> None:
        self._database = database
        self._app = app

    async def run(self):
        """Запуск."""
        await self._database.connect()
        await self._app.run()
