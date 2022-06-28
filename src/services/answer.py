from pydantic import BaseModel


class AnswerInterface(object):
    """Интерфейс для отсылаемых объектов."""

    async def send(self, chat_id: int):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError


class Answer(BaseModel, AnswerInterface):
    """Ответ пользователю."""

    chat_id: int
    message: str

    async def send(self, chat_id: int):
        """Метод для отправки ответа.

        :param chat_id: int
        """
        pass  # noqa: WPS420


class AnswersList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        super().__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        """
        for elem in self:
            elem.send(chat_id)
