import httpx
from databases import Database

from db.connection import database
from integrations.tg.tg_answers import (
    TgAnswerInterface,
    TgAnswerMarkup,
    TgChatIdAnswer,
    TgKeyboardEditAnswer,
    TgMessageIdAnswer,
)
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from services.ayats.ayat_answer import FavoriteAyatAnswerKeyboard
from services.ayats.favorite_ayats import FavoriteAyatStatus
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface
from services.regular_expression import IntableRegularExpression


class ChangeFavoriteAyatAnswer(TgAnswerInterface):
    """Ответ на запрос о смене аята в избранном."""

    def __init__(self, ayat_search: AyatSearchInterface, connection: Database, answer: TgAnswerInterface):
        self._ayat_search = ayat_search
        self._origin = answer
        self._connection = connection

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
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
        await self._connection.execute(
            query, {'ayat_id': status.ayat_id(), 'user_id': update.chat_id()},
        )
        return await TgChatIdAnswer(
            TgMessageIdAnswer(
                TgAnswerMarkup(
                    TgKeyboardEditAnswer(self._origin),
                    FavoriteAyatAnswerKeyboard(
                        result_ayat, FavoriteAyatsRepository(database),
                    ),
                ),
                update.callback_query.message.message_id,
            ),
            update.chat_id(),
        ).build(update)
