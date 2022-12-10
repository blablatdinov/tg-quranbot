import httpx

from app_types.stringable import Stringable
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgAudioAnswer(TgAnswerInterface):
    """Ответ с аудио файлом."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Создание.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.join('sendAudio'))
            for request in await self._origin.build(update)
        ]
