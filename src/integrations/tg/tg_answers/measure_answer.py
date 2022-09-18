import time

import httpx
from loguru import logger

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgMeasureAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        start = time.time()
        requests = await self._origin.build(update)
        logger.info('Update <{0}> process time: {1}'.format(update.update_id, time.time() - start))
        return requests
