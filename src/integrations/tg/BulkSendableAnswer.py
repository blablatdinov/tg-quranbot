from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.SendableAnswer import SendableAnswer
from integrations.tg.UserNotSubscribedSafeSendable import UserNotSubscribedSafeSendable
from integrations.tg.sendable import Sendable
from integrations.tg.tg_answers.tg_answer import TgAnswer


import attrs


import asyncio
from itertools import chain
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
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
        tasks = [
            UserNotSubscribedSafeSendable(
                SendableAnswer(answer, self._logger),
            ).send(update)
            for answer in self._answers
        ]
        responses: list[dict] = []
        for sendable_slice in distribute(10, tasks):
            res_list = await asyncio.gather(*sendable_slice)
            for res in chain.from_iterable(res_list):
                responses.append(res)  # noqa: PERF402
        return responses