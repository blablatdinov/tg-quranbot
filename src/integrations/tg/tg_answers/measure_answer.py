"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from pyeo import elegant
import time
from typing import final

import attrs
import httpx
from loguru import logger

from app_types.floatable import Floatable
from app_types.update import Update
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.update_id import UpdateId


@final
@attrs.define(frozen=True)
@elegant
class Millis(Floatable):
    """Миллисекунды."""

    _millis: float

    @classmethod
    def seconds_ctor(cls, seconds: float):
        """Конструктор для секунд.

        :param seconds: float
        :return: Millis
        """
        return Millis(seconds * 1000)

    def __float__(self):
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return self._millis


@final
@attrs.define(frozen=True)
@elegant
class RoundedFloat(Floatable):
    """Округленное дробное число."""

    _origin: Floatable
    _shift_comma: int

    def __float__(self):
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return round(float(self._origin), self._shift_comma)


@final
@attrs.define(frozen=True)
@elegant
class TgMeasureAnswer(TgAnswerInterface):
    """Замеренный ответ."""

    _origin: TgAnswerInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :returns: list[httpx.Request]
        """
        start = time.time()
        logger.info('Start process update <{0}>'.format(int(UpdateId(update))))
        requests = await self._origin.build(update)
        logger.info('Update <{0}> process time: {1} ms'.format(
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
