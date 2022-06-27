class AdminMessageRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, key: str) -> str:
        """Метод для получения административного сообщения.

        :param key: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AdminMessageRepository(AdminMessageRepositoryInterface):

    def __init__(self, connection):
        self.connection = connection

    async def get(self, key: str) -> str:
        record = await self.connection.fetchrow(
            "SELECT text FROM bot_init_adminmessage m WHERE m.key = '{}'".format(key),
        )
        return record['text']
