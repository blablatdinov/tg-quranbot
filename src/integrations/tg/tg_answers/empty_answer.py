import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgEmptyAnswer(TgAnswerInterface):
    """Пустой ответ."""

    def __init__(self, token: str):
        self._token = token

    async def build(self, update) -> list[httpx.Request]:
        """Создать ответ с токеном.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [httpx.Request('GET', httpx.URL('https://api.telegram.org/bot{0}/'.format(self._token)))]
