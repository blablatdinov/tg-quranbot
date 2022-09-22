import httpx

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
        self._origin = answer
        self._debug_mode = debug_mode
        self._podcast = podcast

    async def build(self, update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        return await FileAnswer(
            self._debug_mode,
            TelegramFileIdAnswer(
                TgChatIdAnswer(
                    TgAudioAnswer(
                        self._origin,
                    ),
                    update._message.chat.id,
                ),
                await self._podcast.audio_telegram_id(),
            ),
            TgTextAnswer(
                TgChatIdAnswer(
                    TgMessageAnswer(
                        self._origin,
                    ),
                    update._message.chat.id,
                ),
                await self._podcast.link_to_audio_file(),
            ),
        ).build(update)
