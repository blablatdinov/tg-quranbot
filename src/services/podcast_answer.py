import httpx

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from repository.podcast import RandomPodcastInterface
from services.answers.answer import FileAnswer, TelegramFileIdAnswer


class PodcastAnswer(TgAnswerInterface):
    """Ответ с подкастом."""

    def __init__(self, debug_mode: bool, answer: TgAnswerInterface, podcast: RandomPodcastInterface):
        """Конструктор класса.

        :param debug_mode: bool
        :param answer: TgAnswerInterface
        :param podcast: RandomPodcastInterface
        """
        self._origin = answer
        self._debug_mode = debug_mode
        self._podcast = podcast

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Stringable
        :return: AnswerInterface
        """
        chat_id = int(TgChatId(update))
        return await FileAnswer(
            self._debug_mode,
            TelegramFileIdAnswer(
                TgChatIdAnswer(
                    TgAudioAnswer(
                        self._origin,
                    ),
                    chat_id,
                ),
                await self._podcast.audio_telegram_id(),
            ),
            TgTextAnswer(
                TgChatIdAnswer(
                    TgMessageAnswer(
                        self._origin,
                    ),
                    chat_id,
                ),
                await self._podcast.link_to_audio_file(),
            ),
        ).build(update)
