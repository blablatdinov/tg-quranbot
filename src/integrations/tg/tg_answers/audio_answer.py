import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class AudioAnswer(TgAnswerInterface):
    """Ответ с аудио файлом."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Создание.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.join('sendAudio'))
            for request in await self._origin.build(update)
        ]
