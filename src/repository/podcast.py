from typing import Optional

from databases import Database
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


class PodcastRepository(PodcastRepositoryInterface):
    """Класс для работы с хранилищем подкастов."""

    def __init__(self, connection: Database):
        self.connection = connection

    async def get_random(self) -> Podcast:
        """Получить случайный подкаст.

        :returns: Podcast
        """
        query = """
            SELECT
                f.telegram_file_id as audio_telegram_id,
                f.link as link_to_audio_file
            FROM qbot_aiogram.public.podcasts p
            INNER JOIN files f on p.file_id = f.file_id
            ORDER BY random()
            LIMIT 1
        """
        row = await self.connection.fetch_one(query)
        return Podcast.parse_obj(row._mapping)  # noqa: WPS437
