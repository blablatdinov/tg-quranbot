from repository.ayats.ayat import Ayat, AyatRepositoryInterface


class AyatRepositoryMock(AyatRepositoryInterface):
    storage: list[Ayat] = []

    async def get_ayat_by_sura_ayat_num(self, sura_num: str, ayat_num: str) -> Ayat:
        return list(
            filter(
                lambda ayat: self._filter_by_sura_and_ayat_num(ayat, sura_num, ayat_num), self.storage,
            ),
        )[0]

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        return list(
            filter(
                lambda ayat: str(ayat.sura_num) == str(sura_num), self.storage,
            ),
        )

    async def get(self, ayat_id: int) -> Ayat:
        return list(
            filter(
                lambda ayat: ayat.id == ayat_id,
                self.storage,
            ),
        )[0]

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        return True

    def _filter_by_sura_and_ayat_num(self, ayat: Ayat, sura_num: str, ayat_num: str) -> bool:
        coincidence_by_sura_num = str(ayat.sura_num) == str(sura_num)
        coincidence_by_ayat_num = str(ayat.ayat_num) == str(ayat_num)
        return coincidence_by_sura_num and coincidence_by_ayat_num
