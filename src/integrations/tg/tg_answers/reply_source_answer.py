import httpx

from app_types.stringable import Stringable
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import TgAnswerInterface


class TgReplySourceAnswer(TgAnswerInterface):
    """Ответ на сообщение."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('reply_to_message_id', int(MessageId(update))),
            )
            for request in await self._origin.build(update)
        ]
