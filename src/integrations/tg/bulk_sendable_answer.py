# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
from typing import final, override

import attrs
from more_itertools import flatten

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.sendable import Sendable
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.user_not_subscribed_safe_sendable import UserNotSubscribedSafeSendable


@final
@attrs.define(frozen=True)
class BulkSendableAnswer(Sendable):
    """Массовая отправка."""

    _answers: list[TgAnswer]
    _logger: LogSink

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[dict]
        """
        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(
                    UserNotSubscribedSafeSendable(
                        SendableAnswer(answer, self._logger),
                    ).send(update),
                )
                for answer in self._answers
            ]
        return list(flatten([task.result() for task in tasks]))
