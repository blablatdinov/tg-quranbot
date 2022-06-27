class AdminMessageRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, key: str) -> str:
        """Метод для получения административного сообщения.

        :param key: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
