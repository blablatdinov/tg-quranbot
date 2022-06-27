from pydantic import BaseModel


class Ayat(BaseModel):
    """Модель аята."""

    sura_num: int
    ayat_num: str
    arab_text: str
    content: str  # noqa: WPS110 wrong variable name
    transliteration: str


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
