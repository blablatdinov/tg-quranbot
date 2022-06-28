import datetime
from dataclasses import dataclass

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


@dataclass
class PrayerTimeRepository(PrayerTimeRepositoryInterface):

    def __init__(self, connection):
        self.connection = connection

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
        city_id: int,
    ) -> list[Prayer]:
        query = """
            SELECT
                c.name as city,
                d.date as day,
                p.time as time,
                p.name as name
            FROM prayer_prayer p
            INNER JOIN bot_init_subscriber s on p.city_id = s.city_id
            INNER JOIN prayer_city c on p.city_id = c.id
            INNER JOIN prayer_day d on p.day_id = d.id
            where s.tg_chat_id = $1 and d.date = $2
        """
        rows = await self.connection.fetch(query, chat_id, target_datetime)
        return [
            Prayer(**dict(row))
            for row in rows
        ]

