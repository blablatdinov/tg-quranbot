from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class Podcast(BaseModel):

    audio_telegram_id: Optional[str]
    link_to_audio_file: str


class PodcastRepositoryInterface(object):

    async def get_random(self) -> Podcast:
        raise NotImplementedError


@dataclass
class PodcastRepository(PodcastRepositoryInterface):

    def __init__(self, connection):
        self.connection = connection

    async def get_random(self):
        query = """
            SELECT
                f.tg_file_id as audio_telegram_id,
                f.link_to_file as link_to_audio_file
            FROM content_podcast p
            inner join content_file f on p.audio_id = f.id
            ORDER BY random()
            LIMIT 1
        """
        row = await self.connection.fetchrow(query)
        return Podcast(**dict(row))
