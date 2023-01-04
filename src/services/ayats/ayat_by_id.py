import httpx

from app_types.stringable import Stringable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgTextAnswer
from services.answers.answer import FileAnswer, TelegramFileIdAnswer
from services.ayats.ayat_by_id_message_answer import AyatByIdMessageAnswer
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface
from services.regular_expression import IntableRegularExpression


class AyatByIdAnswer(TgAnswerInterface):
    """Ответ на аят по идентификатору."""

    def __init__(
        self,
        debug_mode: bool,
        ayat_search: AyatSearchInterface,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
    ):
        """Конструктор класса.

        :param debug_mode: bool
        :param ayat_search: AyatSearchInterface
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        """
        self._debug_mode = debug_mode
        self._ayat_search = ayat_search
        self._message_answer = message_answer
        self._file_answer = file_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = await self._ayat_search.search(
            int(IntableRegularExpression(str(CallbackQueryData(update)))),
        )
        return await TgAnswerList(
            AyatByIdMessageAnswer(
                result_ayat, self._message_answer,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    result_ayat.audio_telegram_id,
                ),
                TgTextAnswer(
                    self._message_answer,
                    result_ayat.link_to_audio_file,
                ),
            ),
        ).build(update)
