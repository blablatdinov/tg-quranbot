import httpx

from db.connection import database
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.answers.answer import FileAnswer, TelegramFileIdAnswer
from services.ayats.search_by_sura_ayat_num import (
    AyatFavoriteKeyboardButton,
    AyatNeighborAyatKeyboard,
    AyatSearchInterface, AyatCallbackTemplate,
)
from services.regular_expression import IntableRegularExpression


class AyatByIdAnswer(TgAnswerInterface):

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

    async def build(self, update: Update) -> list[httpx.Request]:
        result_ayat = await self._ayat_search.search(
            int(IntableRegularExpression(update.callback_query.data)),
        )
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(result_ayat),
                ),
                AyatFavoriteKeyboardButton(
                    result_ayat,
                    AyatNeighborAyatKeyboard(
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
