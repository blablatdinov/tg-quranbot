import httpx

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgReplySourceAnswer(TgAnswerInterface):
    """Ответ на сообщение."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :returns: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('reply_to_message_id', update.message_id()))
            for request in await self._origin.build(update)
        ]
