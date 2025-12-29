# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import time
from typing import final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.millis import Millis
from app_types.rounded_float import RoundedFloat
from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.update_id import UpdateId


@final
@attrs.define(frozen=True)
class TgMeasureAnswer(TgAnswer):
    """Замеренный ответ."""

    _origin: TgAnswer
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :returns: list[httpx.Request]
        """
        start = time.time()
        self._logger.info('Start process update <{0}>'.format(int(UpdateId(update))))
        requests = await self._origin.build(update)
        self._logger.info('Update <{0}> process time: {1:.2f} ms'.format(
            int(UpdateId(update)),
            float(
                RoundedFloat(
                    Millis.seconds_ctor(
                        time.time() - start,
                    ),
                    2,
                ),
            ),
        ))
        return requests
