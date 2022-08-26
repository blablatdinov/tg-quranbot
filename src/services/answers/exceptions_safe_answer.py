from aiogram import Bot, types

from exceptions.base_exception import BaseAppError
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.interface import AnswerInterface


class ExceptionSafeAnswer(AnswerInterface):
    """Обработка ошибок для ответов."""

    _origin: AnswerInterface

    def __init__(self, answerable: AnswerInterface, bot: Bot, chat_id: int):
        self._origin = answerable
        self._bot = bot
        self._chat_id = chat_id

    async def send(self) -> list[types.Message]:
        """Трансформация в ответ.

        :return: AnswerInterface
        """
        try:
            return await self._origin.send()
        except BaseAppError as error:
            if error.user_message:
                return await TextAnswer(
                    self._bot, self._chat_id, error.user_message, DefaultKeyboard(),
                ).send()
        return []
