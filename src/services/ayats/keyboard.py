from aiogram import types
from loguru import logger

from exceptions import AyatHaveNotNeighborsError
from repository.ayats.ayat import AyatNeighbors
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard_interface import AyatSearchKeyboardInterface

CALLBACK_DATA_ADD_TO_FAVORITE_TEMPLATE = 'add_to_favorite({ayat_id})'
CALLBACK_DATA_REMOVE_FROM_FAVORITE_TEMPLATE = 'remove_from_favorite({ayat_id})'


class AyatSearchKeyboard(AyatSearchKeyboardInterface):
    """Клавиатура, выводимая пользователям вместе с найденными аятами."""

    _ayat_search: AyatSearchInterface
    _favorite_ayats_repository: FavoriteAyatRepositoryInterface
    _chat_id: int
    _pagination_buttons_keyboard: AyatPaginatorCallbackDataTemplate

    def __init__(
        self,
        ayat_search: AyatSearchInterface,
        favorite_ayats_repository: FavoriteAyatRepositoryInterface,
        chat_id: int,
        pagination_buttons_keyboard: AyatPaginatorCallbackDataTemplate,
    ):
        self._ayat_search = ayat_search
        self._favorite_ayats_repository = favorite_ayats_repository
        self._chat_id = chat_id
        self._pagination_buttons_keyboard = pagination_buttons_keyboard

    async def generate(self) -> types.InlineKeyboardMarkup:
        """Генерация клавиатуры.

        :returns: InlineKeyboard
        :raises AyatHaveNotNeighborsError: если переданы аяты с пустыми соседями
        """
        ayat = await self._ayat_search.search()
        ayat_neighbors = ayat.find_neighbors()
        if not ayat_neighbors.left and not ayat_neighbors.right:
            raise AyatHaveNotNeighborsError
        ayat_is_favorite = await self._favorite_ayats_repository.check_ayat_is_favorite_for_user(ayat.id, self._chat_id)
        if ayat_is_favorite:
            favorite_button = types.InlineKeyboardButton(
                text='Удалить из избранного',
                callback_data=CALLBACK_DATA_REMOVE_FROM_FAVORITE_TEMPLATE.format(ayat_id=ayat.id),
            )
        else:
            favorite_button = types.InlineKeyboardButton(
                text='Добавить в избранное',
                callback_data=CALLBACK_DATA_ADD_TO_FAVORITE_TEMPLATE.format(ayat_id=ayat.id),
            )

        if self._is_first_ayat(ayat_neighbors):
            return self._first_ayat_case(ayat_neighbors, favorite_button)
        elif self._is_last_ayat(ayat_neighbors):
            return self._last_ayat_case(ayat_neighbors, favorite_button)

        return self._middle_ayat_case(ayat_neighbors, favorite_button)

    def _is_first_ayat(self, ayat_neighbors: AyatNeighbors) -> bool:
        return not ayat_neighbors.left

    def _is_last_ayat(self, ayat_neighbors: AyatNeighbors) -> bool:
        return not ayat_neighbors.right

    def _first_ayat_case(self, neighbor_ayats: AyatNeighbors, favorite_button: types.InlineKeyboardButton) -> types.InlineKeyboardMarkup:
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=neighbor_ayats.right.title(),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=neighbor_ayats.right.id),
                ),
            )
            .row(favorite_button)
        )

    def _last_ayat_case(
        self, neighbor_ayats: AyatNeighbors, favorite_button: types.InlineKeyboardButton) -> types.InlineKeyboardMarkup:
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=neighbor_ayats.left.title(),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=neighbor_ayats.left.id),
                ),
            )
            .row(favorite_button)
        )

    def _middle_ayat_case(
        self,
        neighbor_ayats:
        AyatNeighbors,
        favorite_button: types.InlineKeyboardButton,
    ) -> types.InlineKeyboardMarkup:
        logger.debug(str(neighbor_ayats))
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=neighbor_ayats.left.title(),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=neighbor_ayats.left.id),
                ),
                types.InlineKeyboardButton(
                    text=neighbor_ayats.right.title(),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=neighbor_ayats.right.id),
                ),
            )
            .row(favorite_button)
        )
