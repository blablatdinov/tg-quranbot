from app_types.stringable import Stringable
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from repository.ayats.schemas import Ayat
from services.answers.answer import KeyboardInterface
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard


class AyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    def __init__(
        self,
        ayat: Ayat,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
        neighbor_ayats: NeighborAyatsRepositoryInterface,
    ):
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo
        self._neighbor_ayats = neighbor_ayats

    async def generate(self, update: Stringable) -> str:
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(self._neighbor_ayats, AyatCallbackTemplate.get_ayat),
            self._favorite_ayats_repo,
        ).generate(update)
