from aiogram import types
from aiogram.dispatcher import FSMContext

from services.answers.interface import AnswerInterface


class StateFinishAnswer(AnswerInterface):
    """Класс ответа с обнулением состояния."""

    def __init__(self, answer: AnswerInterface, state: FSMContext):
        self._origin = answer
        self._state = state

    async def send(self) -> list[types.Message]:
        """Отправка.

        :return: list[types.Message]
        """
        messages = await self._origin.send()
        await self._state.finish()
        return messages
