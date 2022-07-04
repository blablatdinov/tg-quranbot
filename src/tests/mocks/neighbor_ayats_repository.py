from repository.ayats.ayat import Ayat
from repository.ayats.neighbor_ayats import AyatShort, NeighborAyatsRepositoryInterface


class NeighborAyatsRepositoryMock(NeighborAyatsRepositoryInterface):
    storage: list[AyatShort]

    def __init__(self, ayats_storage: list[Ayat] = None):
        if ayats_storage is None:
            self.storage = []
            return
        self.storage = [
            AyatShort(id=ayat.id, sura_num=ayat.sura_num, ayat_num=ayat.ayat_num)
            for ayat in ayats_storage
        ]

    async def get_ayat_neighbors(self, ayat_id: int) -> list[AyatShort]:
        if ayat_id == self.storage[0].id:
            return self.storage[:2]
        elif ayat_id == self.storage[-1].id:
            return self.storage[-2:]

        # find index
        index = 0
        for storage_index, ayat in enumerate(self.storage):  # noqa: B007
            if ayat.id == ayat_id:
                index = storage_index
                break

        return self.storage[index - 1:index + 2]
