from aiogram import Bot, types

from repository.podcast import PodcastRepositoryInterface
from services.answers.answer import FileAnswer, TelegramFileIdAnswer, FileLinkAnswer, DefaultKeyboard
from services.answers.interface import AnswerInterface


class PodcastAnswer(AnswerInterface):
    """Ответ с подкастом."""

    _podcast_repository: PodcastRepositoryInterface

    def __init__(self, debug_mode: bool, chat_id: int, bot: Bot, podcast_repository: PodcastRepositoryInterface):
        self._debug_mode = debug_mode
        self._chat_id = chat_id
        self._bot = bot
        self._podcast_repository = podcast_repository

    async def send(self) -> list[types.Message]:
        """Трансформация в ответ.

        :return: AnswerInterface
        """
        podcast = await self._podcast_repository.get_random()
        return await FileAnswer(
            self._debug_mode,
            TelegramFileIdAnswer(
                self._bot,
                self._chat_id,
                podcast.audio_telegram_id,
                DefaultKeyboard(),
            ),
            FileLinkAnswer(
                self._bot,
                self._chat_id,
                podcast.link_to_audio_file,
                DefaultKeyboard(),
            ),
        ).send()
