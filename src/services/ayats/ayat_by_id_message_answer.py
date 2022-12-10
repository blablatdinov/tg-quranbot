import httpx

from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgTextAnswer
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from repository.ayats.schemas import Ayat
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard


class AyatByIdMessageAnswer(TgAnswerInterface):
    """Текстовый ответ на поиск аята."""

    def __init__(self, result_ayat: Ayat, message_answer: TgAnswerInterface):
        """Конструктор класса.

        :param result_ayat: Ayat
        :param message_answer: TgAnswerInterface
        """
        self._result_ayat = result_ayat
        self._message_answer = message_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return await TgAnswerMarkup(
            TgTextAnswer(
                self._message_answer,
                str(self._result_ayat),
            ),
            AyatFavoriteKeyboardButton(
                self._result_ayat,
                NeighborAyatKeyboard(
                    NeighborAyats(database, self._result_ayat.id),
                    AyatCallbackTemplate.get_ayat,
                ),
                FavoriteAyatsRepository(database),
            ),
        ).build(update)
