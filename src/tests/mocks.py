import random
from typing import Optional

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats import AyatRepositoryInterface, Ayat
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
            User(id=user_id, is_active=True, day=2, referrer=referrer_id, chat_id=chat_id),
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
                lambda ayat: str(ayat.sura_num) == str(sura_num) and str(ayat.ayat_num) == str(ayat_num), self.storage,
            ),
        )[0]

    async def get_ayats_by_sura_num(self, sura_num: str) -> list[Ayat]:
        return list(
            filter(
                lambda ayat: str(ayat.sura_num) == str(sura_num), self.storage
            ),
        )


class AyatServiceMock(AyatServiceInterface):

    async def get_formatted_first_ayat(self):
        return 'some string'
