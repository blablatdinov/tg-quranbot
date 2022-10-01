import httpx

from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerMarkup, TgTextAnswer
from repository.ayats.schemas import Ayat
from services.answers.answer import FileAnswer, KeyboardInterface, TelegramFileIdAnswer


class AyatAnswer(TgAnswerInterface):
    """Ответ с аятом."""

    def __init__(
        self,
        debug: bool,
        answers: tuple[TgAnswerInterface, TgAnswerInterface],
        ayat: Ayat,
        ayat_answer_keyboard: KeyboardInterface,
    ):
        self._debug_mode = debug
        self._message_answer = answers[0]
        self._file_answer = answers[1]
        self._ayat = ayat
        self._ayat_answer_keyboard = ayat_answer_keyboard

    async def build(self, update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(self._ayat),
                ),
                self._ayat_answer_keyboard,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    self._ayat.audio_telegram_id,
                ),
                TgTextAnswer(
                    self._message_answer,
                    self._ayat.link_to_audio_file,
                ),
            ),
        ).build(update)
