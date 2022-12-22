import httpx

from app_types.stringable import Stringable
from integrations.tg.tg_answers import TgAnswerInterface
from repository.admin_message import AdminMessageInterface


class HelpAnswer(TgAnswerInterface):
    """Ответ на команду /help."""

    def __init__(self, answer: TgAnswerInterface, admin_message: AdminMessageInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param admin_message: AdminMessageInterface
        """
        self._origin = answer
        self._admin_message = admin_message

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('text', await self._admin_message.text()),
            )
            for request in await self._origin.build(update)
        ]
