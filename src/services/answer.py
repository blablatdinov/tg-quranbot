from pydantic import BaseModel


class AnswerInterface(object):

    async def send(self, chat_id: int):
        raise NotImplementedError


class Answer(BaseModel, AnswerInterface):
    chat_id: int
    message: str

    async def send(self, chat_id: int):
        pass


class AnswersList(list, AnswerInterface):
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        super(AnswersList, self).__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки сообщений."""
        for elem in self:
            elem.send(chat_id)
