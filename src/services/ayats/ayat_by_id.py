from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface


class AyatById(AyatSearchInterface):
    """Аят по идентификатору."""

    _ayat_repository: AyatRepositoryInterface
    _ayat_id: int

    def __init__(self, ayat_repository: AyatRepositoryInterface, ayat_id: int):
        self._ayat_repository = ayat_repository
        self._ayat_id = ayat_id

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск по идентификатору.

        :returns: Ayat
        """
        return await self._ayat_repository.get(self._ayat_id)
