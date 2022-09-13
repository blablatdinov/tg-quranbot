import httpx

from integrations.tg.tg_answers.audio_answer import AudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from repository.podcast import PodcastRepositoryInterface
from services.answers.answer import FileAnswer, TelegramFileIdAnswer


class PodcastAnswer(TgAnswerInterface):
    """Ответ с подкастом."""

    _podcast_repository: PodcastRepositoryInterface

    def __init__(self, debug_mode: bool, answer: TgAnswerInterface, podcast_repository: PodcastRepositoryInterface):
        self._origin = answer
        self._debug_mode = debug_mode
        self._podcast_repository = podcast_repository

    async def build(self, update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :return: AnswerInterface
        """
        podcast = await self._podcast_repository.get_random()
        return await FileAnswer(
            self._debug_mode,
            TelegramFileIdAnswer(
                TgChatIdAnswer(
                    AudioAnswer(
                        self._origin,
                    ),
                    update.message.chat.id,
                ),
                podcast.audio_telegram_id,
            ),
            TgTextAnswer(
                TgChatIdAnswer(
                    TgMessageAnswer(
                        self._origin,
                    ),
                    update.message.chat.id,
                ),
                podcast.link_to_audio_file,
            ),
        ).build(update)
