from aiogram import types

from services.answers.interface import AnswerInterface


class AnswersList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        super().__init__(args)

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :return: list[types.Message]
        """
        messages: list[types.Message] = []
        for elem in self:
            messages = sum([messages, await elem.send()], start=[])
        return messages
