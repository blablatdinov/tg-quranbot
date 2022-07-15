from dataclasses import dataclass
from typing import Optional

from asyncpg import Connection
from pydantic import BaseModel


class Podcast(BaseModel):
    """Модель подкаста."""

    audio_telegram_id: Optional[str]
    link_to_audio_file: str


class PodcastRepositoryInterface(object):
    """Интерфейс для работы с хранилищем подкастов."""

    async def get_random(self) -> Podcast:
        """Получить случайный подкаст.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class PodcastRepository(PodcastRepositoryInterface):
    """Класс для работы с хранилищем подкастов."""

    def __init__(self, connection: Connection):
        self.connection = connection

    async def get_random(self) -> Podcast:
        """Получить случайный подкаст.

        :returns: Podcast
        """
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
        return Podcast.parse_obj(row)
