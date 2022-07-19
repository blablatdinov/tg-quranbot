from app_types.answerable import Answerable
from repository.podcast import PodcastRepositoryInterface
from services.answers.answer import Answer
from services.answers.interface import AnswerInterface


class PodcastAnswer(Answerable):
    """Ответ с подкастом."""

    _podcast_repository: PodcastRepositoryInterface

    def __init__(self, podcast_repository: PodcastRepositoryInterface):
        self._podcast_repository = podcast_repository

    async def to_answer(self) -> AnswerInterface:
        """Трансформация в ответ.

        :return: AnswerInterface
        """
        podcast = await self._podcast_repository.get_random()
        return Answer(
            telegram_file_id=podcast.audio_telegram_id,
            link_to_file=podcast.link_to_audio_file,
        )
