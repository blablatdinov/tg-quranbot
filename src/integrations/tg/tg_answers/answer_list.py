import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgAnswerList(TgAnswerInterface):
    """Список ответов пользователю."""

    def __init__(self, *answers: TgAnswerInterface):
        self._answers = answers

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        rebuilded_requests = []
        for answer in self._answers:
            answer_requests = await answer.build(update)
            rebuilded_requests += answer_requests

        return rebuilded_requests
