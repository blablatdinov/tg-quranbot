# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import time
from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.millis import Millis
from app_types.rounded_float import RoundedFloat
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerToSender, TgMessageAnswer, TgTextAnswer


@final
@attrs.define(frozen=True)
class StatusAnswer(TgAnswer):
    """Ответ со статусом системы."""

    _empty_answer: TgAnswer
    _pgsql: AsyncEngine
    _redis: Redis

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgTextAnswer.str_ctor(
            TgAnswerToSender(
                TgMessageAnswer(self._empty_answer),
            ),
            '{0}\n{1}'.format(
                await self._measure_pgsql(),
                await self._measure_redis(),
            ),
        ).build(update)

    async def _measure_pgsql(self) -> str:  # noqa: NPM100. Fix it
        db_start = time.time()
        async with self._pgsql.connect() as conn:
            await conn.execute(text('SELECT 1'))
        return 'DB: {0} ms'.format(float(
            RoundedFloat(
                Millis.seconds_ctor(time.time() - db_start),
                2,
            ),
        ))

    async def _measure_redis(self) -> str:  # noqa: NPM100. Fix it
        redis_start = time.time()
        await self._redis.ping()
        return 'Redis: {0} ms'.format(float(
            RoundedFloat(
                Millis.seconds_ctor(time.time() - redis_start),
                2,
            ),
        ))
