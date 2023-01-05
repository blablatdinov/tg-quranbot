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
import time

import httpx
from loguru import logger

from app_types.floatable import Floatable
from app_types.stringable import Stringable
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.update_id import UpdateId


class Millis(Floatable):
    """Миллисекунды."""

    def __init__(self, millis: float):
        """Конструктор класса.

        :param millis: float
        """
        self._millis = millis

    @classmethod
    def seconds_cs(cls, seconds: float):
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


class RoundedFloat(Floatable):
    """Округленное дробное число."""

    def __init__(self, origin_float: Floatable, shift_comma: int):
        """Конструктор класса.

        :param origin_float: Floatable
        :param shift_comma: int
        """
        self._origin = origin_float
        self._shift_comma = shift_comma

    def __float__(self):
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return round(float(self._origin), self._shift_comma)


class TgMeasureAnswer(TgAnswerInterface):
    """Замеренный ответ."""

    def __init__(self, answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        """
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        start = time.time()
        logger.info('Start process update <{0}>'.format(int(UpdateId(update))))
        requests = await self._origin.build(update)
        logger.info('Update <{0}> process time: {1} ms'.format(
            int(UpdateId(update)),
            float(
                RoundedFloat(
                    Millis.seconds_cs(
                        time.time() - start,
                    ),
                    2,
                ),
            ),
        ))
        return requests
