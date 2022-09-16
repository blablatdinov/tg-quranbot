import httpx
from databases import Database

from db.connection import database
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from integrations.tg.tg_answers.message_keyboard_edit_answer import TgKeyboardEditAnswer
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.ayats.search_by_sura_ayat_num import (
    AyatFavoriteKeyboardButton,
    AyatNeighborAyatKeyboard,
    AyatSearchInterface,
)
from services.regular_expression import IntableRegularExpression


class FavoriteAyatStatus(object):

    def __init__(self, source: str):
        self._source = source

    def ayat_id(self) -> int:
        return int(IntableRegularExpression(self._source))

    def change_to(self):
        return 'addToFavor' in self._source


class FavoriteAyatAnswer(TgAnswerInterface):

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
                        ),
                        FavoriteAyatsRepository(database),
                    )
                ),
                update.callback_query.message.message_id,
            ),
            update.chat_id(),
        ).build(update)
