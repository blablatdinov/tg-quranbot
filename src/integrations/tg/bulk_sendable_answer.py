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
from itertools import chain
from typing import final, override

import attrs
from more_itertools import distribute
from pyeo import elegant

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.sendable import Sendable
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.user_not_subscribed_safe_sendable import UserNotSubscribedSafeSendable


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
