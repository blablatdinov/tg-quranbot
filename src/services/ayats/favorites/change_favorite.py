import httpx
from databases import Database

from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import (
    TgAnswerInterface,
    TgAnswerMarkup,
    TgChatIdAnswer,
    TgKeyboardEditAnswer,
    TgMessageIdAnswer,
)
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.favorite_ayats import FavoriteAyatStatus
from services.ayats.keyboards import AyatAnswerKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface
from services.regular_expression import IntableRegularExpression


class ChangeFavoriteAyatAnswer(TgAnswerInterface):
    """Ответ на запрос о смене аята в избранном."""

    def __init__(
        self,
        ayat_search: AyatSearchInterface,
        connection: Database,
        answer: TgAnswerInterface,
    ):
        """Конструктор класса.

        :param ayat_search: AyatSearchInterface
        :param connection: Database
        :param answer: TgAnswerInterface
        """
        self._ayat_search = ayat_search
        self._origin = answer
        self._connection = connection

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        status = FavoriteAyatStatus(str(CallbackQueryData(update)))
        result_ayat = await self._ayat_search.search(
            int(IntableRegularExpression(str(CallbackQueryData(update)))),
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
            query, {'ayat_id': status.ayat_id(), 'user_id': int(TgChatId(update))},
        )
        return await TgChatIdAnswer(
            TgMessageIdAnswer(
                TgAnswerMarkup(
                    TgKeyboardEditAnswer(self._origin),
                    AyatAnswerKeyboard(
                        result_ayat,
                        FavoriteAyatsRepository(database),
                        NeighborAyats(
                            database, result_ayat.id,
                        ),
                        AyatCallbackTemplate.get_favorite_ayat,
                    ),
                ),
                int(MessageId(update)),
            ),
            int(TgChatId(update)),
        ).build(update)
