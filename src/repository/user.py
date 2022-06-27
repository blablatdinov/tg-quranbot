class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    def create(self, chat_id: int):
        """Метод для создания пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
