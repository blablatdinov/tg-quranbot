class AdminMessageRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, key: str) -> str:
        """Метод для получения административного сообщения.

        :param key: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AdminMessageRepository(AdminMessageRepositoryInterface):
    """Класс для работы с БД."""

    def __init__(self, connection):
        self.connection = connection

    async def get(self, key: str) -> str:
        """Получить административное сообщение по ключу.

        :param key: str
        :returns: str
        """
        record = await self.connection.fetchrow(
            "SELECT text FROM bot_init_adminmessage m WHERE m.key = '$1'", key,
        )
        return record['text']
