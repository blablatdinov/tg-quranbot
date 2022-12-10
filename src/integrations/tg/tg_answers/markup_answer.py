import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface
from services.answers.answer import KeyboardInterface


class TgAnswerMarkup(TgAnswerInterface):
    """Ответ с клавиатурой."""

    def __init__(self, answer: TgAnswerInterface, keyboard: KeyboardInterface):
        self._origin = answer
        self._keyboard = keyboard

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ для пользователя.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('reply_markup', await self._keyboard.generate(update)),
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
