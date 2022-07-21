from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate


class AyatSearchInterface(object):
    """Интерфейс класса, осуществляющего поиск аятов."""

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
