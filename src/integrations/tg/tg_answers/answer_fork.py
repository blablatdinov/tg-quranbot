import httpx

from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgAnswerFork(TgAnswerInterface):
    """Маршрутизация ответов."""

    def __init__(self, *answers: TgAnswerInterface):
        self._answers = answers

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises NotProcessableUpdateError: if not found matches
        """
        for answer in self._answers:
            origin_requests = await answer.build(update)
            if origin_requests:
                return origin_requests
        raise NotProcessableUpdateError
