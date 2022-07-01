import random
from typing import Optional

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from repository.ayats.neighbor_ayats import AyatShort, NeighborAyatsRepositoryInterface
from repository.user import User, UserRepositoryInterface
from services.ayat import AyatServiceInterface


class AdminMessageRepositoryMock(AdminMessageRepositoryInterface):

    async def get(self, key: str) -> str:
        return {
            'start': 'start message',
        }[key]


class UserRepositoryMock(UserRepositoryInterface):
    storage: list[User] = []

    async def create(self, chat_id: int, referrer_id: Optional[int]):
        user_id = random.randint(0, 100)
        self.storage.append(
            User(id=user_id, is_active=True, day=2, referrer=referrer_id, chat_id=chat_id, city_id=1),
        )

    async def get_by_id(self, user_id: int) -> User:
        return list(
            filter(
                lambda user: user.id == user_id, self.storage,
            ),
        )[0]

    async def get_by_chat_id(self, chat_id: int) -> User:
        return list(
            filter(
                lambda user: user.chat_id == chat_id, self.storage,
            ),
        )[0]

    async def exists(self, chat_id: int):
        return chat_id in {user.chat_id for user in self.storage}


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

    async def first(self):
        return self.storage[0]

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        return True

    def _filter_by_sura_and_ayat_num(self, ayat: Ayat, sura_num: str, ayat_num: str) -> bool:
        coincidence_by_sura_num = str(ayat.sura_num) == str(sura_num)
        coincidence_by_ayat_num = str(ayat.ayat_num) == str(ayat_num)
        return coincidence_by_sura_num and coincidence_by_ayat_num


class AyatServiceMock(AyatServiceInterface):
    pass


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
