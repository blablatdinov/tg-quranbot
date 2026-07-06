# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
from typing import final, override

import attrs

from app_types.logger import LogSink
from app_types.runable import Runable
from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable import Sendable


@final
@attrs.define(frozen=True)
class PollingApp(Runable):
    """Приложение на long polling."""

    _updates: PollingUpdatesIterator
    _sendable: Sendable
    _logger: LogSink

    @override
    async def run(self) -> None:
        """Запуск."""
        self._logger.info('Start app on polling')
        async with asyncio.TaskGroup() as task_group:
            async for update_list in self._updates:
                for update in update_list:
                    self._logger.debug('Update: {update}', update=update)
                    task_group.create_task(self._sendable.send(update))
