from aiogram import types

from services.answers.interface import AnswerInterface


class AnswersList(AnswerInterface):
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        self._answers = list(args)

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :return: list[types.Message]
        """
        messages: list[types.Message] = []
        for elem in self._answers:
            messages = sum([messages, await elem.send()], start=[])
        return messages
