from services.answers.interface import AnswerInterface


class RegisterInterface(object):
    """Интерфейс объектов, регистрирующих пользователя."""

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def register(self, chat_id: int) -> AnswerInterface:
        """Регистрация.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
