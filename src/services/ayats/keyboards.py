from aioredis import Redis

from db.connection import database
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface, FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats, NeighborAyats, TextSearchNeighborAyatsRepository
from repository.ayats.schemas import Ayat
from services.answers.answer import KeyboardInterface
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard
from services.ayats.ayat_text_search_query import AyatTextSearchQuery


class AyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    def __init__(self, ayat: Ayat, favorite_ayats_repo: FavoriteAyatRepositoryInterface):
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(
                NeighborAyats(
                    database,
                    self._ayat.id,
                ),
                AyatCallbackTemplate.get_ayat,
            ),
            self._favorite_ayats_repo,
        ).generate(update)


class AyatSearchByTextAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята, который ищут текстом."""

    def __init__(self, ayat: Ayat, favorite_ayats_repo: FavoriteAyatRepositoryInterface, redis: Redis):
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo
        self._redis = redis

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(
                TextSearchNeighborAyatsRepository(
                    database,
                    self._ayat.id,
                    AyatTextSearchQuery.for_reading_cs(self._redis, update.chat_id()),
                ),
                AyatCallbackTemplate.get_search_ayat,
            ),
            self._favorite_ayats_repo,
        ).generate(update)


class FavoriteAyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    def __init__(self, ayat: Ayat, favorite_ayats_repo: FavoriteAyatRepositoryInterface):
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(
                FavoriteNeighborAyats(
                    self._ayat.id,
                    update.chat_id(),
                    self._favorite_ayats_repo,
                ),
                AyatCallbackTemplate.get_favorite_ayat,
            ),
            FavoriteAyatsRepository(database),
        ).generate(update)
