import time

import httpx
from loguru import logger

from app_types.floatable import Floatable
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class Millis(Floatable):
    """Миллисекунды."""

    def __init__(self, millis: float):
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
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :returns: list[httpx.Request]
        """
        start = time.time()
        logger.info('Start process update <{0}>'.format(update.update_id))
        requests = await self._origin.build(update)
        logger.info('Update <{0}> process time: {1} ms'.format(
            update.update_id,
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
