import httpx
from databases import Database

from db.connection import database
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from integrations.tg.tg_answers.message_keyboard_edit_answer import TgKeyboardEditAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository, FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyats, FavoriteNeighborAyats
from services.answers.answer import FileAnswer, TelegramFileIdAnswer
from services.ayats.search_by_sura_ayat_num import (
    AyatFavoriteKeyboardButton,
    AyatNeighborAyatKeyboard,
    AyatSearchInterface, AyatCallbackTemplate,
)
from services.regular_expression import IntableRegularExpression


class FavoriteAyatStatus(object):

    def __init__(self, source: str):
        self._source = source

    def ayat_id(self) -> int:
        return int(IntableRegularExpression(self._source))

    def change_to(self):
        return 'addToFavor' in self._source


class ChangeFavoriteAyatAnswer(TgAnswerInterface):

    def __init__(self, ayat_search: AyatSearchInterface, connection: Database, answer: TgAnswerInterface):
        self._ayat_search = ayat_search
        self._origin = answer
        self._connection = connection

    async def build(self, update: Update) -> list[httpx.Request]:
        status = FavoriteAyatStatus(update.callback_query.data)
        result_ayat = await self._ayat_search.search(
            int(IntableRegularExpression(update.callback_query.data)),
        )
        if status.change_to():
            query = """
                INSERT INTO favorite_ayats
                (ayat_id, user_id) 
                VALUES 
                (:ayat_id, :user_id)
            """
        else:
            query = """
                DELETE FROM favorite_ayats
                WHERE ayat_id = :ayat_id AND user_id = :user_id
            """
        await self._connection.execute(query, {'ayat_id': status.ayat_id(), 'user_id': update.chat_id()})
        return await TgChatIdAnswer(
            TgMessageIdAnswer(
                TgAnswerMarkup(
                    TgKeyboardEditAnswer(self._origin),
                    AyatFavoriteKeyboardButton(
                        result_ayat,
                        AyatNeighborAyatKeyboard(
                            NeighborAyats(database, result_ayat.id),
                            AyatCallbackTemplate.get_ayat,
                        ),
                        FavoriteAyatsRepository(database),
                    )
                ),
                update.callback_query.message.message_id,
            ),
            update.chat_id(),
        ).build(update)


class FavoriteAyatAnswer(TgAnswerInterface):

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Update) -> list[httpx.Request]:
        result_ayat = (await self._favorite_ayats_repo.get_favorites(update.chat_id()))[0]
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(result_ayat),
                ),
                AyatFavoriteKeyboardButton(
                    result_ayat,
                    AyatNeighborAyatKeyboard(
                        FavoriteNeighborAyats(
                            result_ayat.id,
                            update.chat_id(),
                            self._favorite_ayats_repo,
                        ),
                        AyatCallbackTemplate.get_favorite_ayat,
                    ),
                    FavoriteAyatsRepository(database),
                )
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


class FavoriteAyatPage(TgAnswerInterface):

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Update) -> list[httpx.Request]:
        result_ayat = await self._favorite_ayats_repo.get_favorite(
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
                        FavoriteNeighborAyats(
                            result_ayat.id,
                            update.chat_id(),
                            self._favorite_ayats_repo,
                        ),
                        AyatCallbackTemplate.get_favorite_ayat,
                    ),
                    FavoriteAyatsRepository(database),
                )
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
