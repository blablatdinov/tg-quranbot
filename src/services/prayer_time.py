from dataclasses import dataclass

from repository.prayer_time import PrayerTimeRepositoryInterface
from services.answer import AnswerInterface


@dataclass
class UserPrayerTimes(object):
    prayer_times_repository: PrayerTimeRepositoryInterface
    chat_id: int

    async def get(self) -> AnswerInterface:
        pass
