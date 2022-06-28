import datetime

from pydantic import BaseModel


class Prayer(BaseModel):
    city: str
    day: datetime.date
    time: datetime.time
    name: str


# TODO: write interface
class PrayerTimeRepositoryInterface(object):

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
        city_id: int,
    ) -> list[Prayer]:
        raise NotImplementedError


# TODO: write implementation
class PrayerTimeRepository(PrayerTimeRepositoryInterface):

    pass
