import datetime
import random
from typing import Optional

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from repository.ayats.neighbor_ayats import AyatShort, NeighborAyatsRepositoryInterface
from repository.podcast import Podcast, PodcastRepositoryInterface
from repository.prayer_time import Prayer, PrayerTimeRepositoryInterface, UserPrayer
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


class PrayerTimeRepositoryMock(PrayerTimeRepositoryInterface):

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
        city_id: int,
    ) -> list[Prayer]:
        date = datetime.datetime(2020, 1, 3)
        times = [
            datetime.time(1, 1),
            datetime.time(3, 1),
            datetime.time(11, 46),
            datetime.time(17, 34),
            datetime.time(20, 32),
            datetime.time(22, 2),
        ]
        names = ['fajr', 'sunrise', 'dhuhr', 'asr', 'magrib', "isha'a"]
        return [
            Prayer(
                id=random.randint(1, 100), city='Казань', day=date, time=time, name=name,
            )
            for time, name in zip(times, names)
        ]

    async def get_user_prayer_times(
        self,
        prayer_ids: list[int],
        chat_id: int,
        date_time: datetime.datetime,
    ) -> list[UserPrayer]:
        return {
            1234: [],
            4321: [UserPrayer(id=prayer_id, is_readed=True) for prayer_id in range(2000, 2006)],
        }.get(chat_id)

    async def create_user_prayer_times(self, prayer_ids: list[int], user_id: int) -> list[UserPrayer]:
        return [
            UserPrayer(id=user_prayer_id, is_readed=True)
            for user_prayer_id in range(1000, 1006)
        ]


class PodcastRepositoryMock(PodcastRepositoryInterface):

    async def get_random(self) -> Podcast:
        return Podcast(audio_telegram_id='file_id', link_to_audio_file='https://link.to.file')
