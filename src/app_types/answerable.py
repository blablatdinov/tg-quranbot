from typing import Protocol

from services.answers.interface import AnswerInterface


class Answerable(Protocol):
    """Интерфейс, сообщающий, что класс может быть трансформирован в ответ."""

    async def to_answer(self) -> AnswerInterface:
        """Трансформация экземпляра в AnswerInterface."""
