from aiogram import types

from services.answers.interface import AnswerInterface, SingleAnswerInterface


class AnswersList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов."""

    def __init__(self, *args: SingleAnswerInterface) -> None:
        super().__init__(args)

    async def send(self, chat_id: int = None) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: list[types.Message]
        """
        messages: list[types.Message] = []
        for elem in self:
            messages = sum([messages, await elem.send(chat_id)], start=[])
        return messages

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        for elem in self:
            await elem.edit_markup(chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return self
