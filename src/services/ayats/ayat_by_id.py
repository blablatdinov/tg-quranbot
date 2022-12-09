import httpx

from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerMarkup, TgTextAnswer
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.answers.answer import FileAnswer, TelegramFileIdAnswer
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard
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
            int(IntableRegularExpression(update.callback_query().data)),
        )
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(result_ayat),
                ),
                AyatFavoriteKeyboardButton(
                    result_ayat,
                    NeighborAyatKeyboard(
                        NeighborAyats(database, result_ayat.id),
                        AyatCallbackTemplate.get_ayat,
                    ),
                    FavoriteAyatsRepository(database),
                ),
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
