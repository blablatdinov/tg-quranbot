import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class HtmlParseAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('parse_mode', 'html'),
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]

