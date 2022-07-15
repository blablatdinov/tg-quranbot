from app_types.intable import Intable
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface


# TODO: test
class AyatById(AyatSearchInterface):
    """Аят по идентификатору."""

    _ayat_repository: AyatRepositoryInterface
    _ayat_id: Intable

    def __init__(self, ayat_repository: AyatRepositoryInterface, ayat_id: Intable):
        self._ayat_repository = ayat_repository
        self._ayat_id = ayat_id

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск по идентификатору.

        :returns: Ayat
        """
        return await self._ayat_repository.get(int(self._ayat_id))
