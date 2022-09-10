import httpx

from services.tg_answers.update import Update


class TgAnswerInterface(object):
    """Интерфейс ответа пользователю."""

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
