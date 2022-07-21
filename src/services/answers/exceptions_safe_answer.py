from app_types.answerable import Answerable
from exceptions.base_exception import BaseAppError
from services.answers.interface import AnswerInterface


class ExceptionSafeAnswer(Answerable):
    """Обработка ошибок для ответов."""

    _origin: Answerable

    def __init__(self, answerable: Answerable):
        self._origin = answerable

    async def to_answer(self) -> AnswerInterface:
        """Трансформация в ответ.

        :return: AnswerInterface
        """
        try:
            return await self._origin.to_answer()
        except BaseAppError as error:
            return await error.to_answer()
