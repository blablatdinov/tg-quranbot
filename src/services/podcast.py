from dataclasses import dataclass

from repository.podcast import Podcast, PodcastRepositoryInterface
from services.answer import Answer


@dataclass
class PodcastService(object):
    """Класс для работы с подкастами."""

    podcast_repository: PodcastRepositoryInterface

    async def get_random(self) -> Podcast:
        """Получить случайный подкаст.

        :returns: Podcast
        """
        return await self.podcast_repository.get_random()


@dataclass
class PodcastAnswer(object):
    """Ответ с подкастом."""

    podcast: Podcast

    def transform(self) -> Answer:
        """Трансформировать подкаст в ответ.

        :returns: Answer
        """
        return Answer(
            telegram_file_id=self.podcast.audio_telegram_id,
            link_to_file=self.podcast.link_to_audio_file,
        )
