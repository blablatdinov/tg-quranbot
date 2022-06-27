from pydantic import BaseModel


class Ayat(BaseModel):
    """Модель аята."""

    pass


class AyatRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, id_: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param id_: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def first(self) -> Ayat:
        """Метод для получения первого аята.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
