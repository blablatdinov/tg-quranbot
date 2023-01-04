import httpx

from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgAnswerMarkup(TgAnswerInterface):
    """Ответ с клавиатурой."""

    def __init__(self, answer: TgAnswerInterface, keyboard: KeyboardInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param keyboard: KeyboardInterface
        """
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
