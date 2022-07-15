from services.answer import AnswerInterface


class Answerable(object):
    """Интерфейс, сообщающий, что класс может быть трансформирован в ответ."""

    async def to_answer(self) -> AnswerInterface:
        """Трансформация экземпляра в AnswerInterface.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
