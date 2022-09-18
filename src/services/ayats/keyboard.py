from aiogram import types

from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import AyatShort
from services.answers.answer import KeyboardInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate

CALLBACK_DATA_ADD_TO_FAVORITE_TEMPLATE = 'add_to_favorite({ayat_id})'
CALLBACK_DATA_REMOVE_FROM_FAVORITE_TEMPLATE = 'remove_from_favorite({ayat_id})'
LEFT_BUTTON_TEXT_TEMPLATE = '⬅️ {0}'
RIGHT_BUTTON_TEXT_TEMPLATE = '{0} ➡️'


class AyatSearchKeyboard(KeyboardInterface):
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
        """
        ayat = await self._ayat_search.search()
        ayat_neighbors = ayat.find_neighbors()
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
        if not ayat_neighbors.left and not ayat_neighbors.right:
            # raise AyatHaveNotNeighborsError
            return self._only_one_ayat_case(favorite_button)

        if not ayat_neighbors.left:
            # ayat_neighbors.right already checked for None value
            return self._first_ayat_case(ayat_neighbors.right, favorite_button)  # type: ignore
        elif not ayat_neighbors.right:
            # ayat_neighbors.left already checked for None value
            return self._last_ayat_case(ayat_neighbors.left, favorite_button)  # type: ignore

        # ayat_neighbors already checked for None value
        return self._middle_ayat_case(ayat_neighbors.left, ayat_neighbors.right, favorite_button)  # type: ignore

    def _first_ayat_case(
        self,
        right_ayat: AyatShort,
        favorite_button: types.InlineKeyboardButton,
    ) -> types.InlineKeyboardMarkup:
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=RIGHT_BUTTON_TEXT_TEMPLATE.format(right_ayat.title()),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=right_ayat.id),
                ),
            )
            .row(favorite_button)
        )

    def _last_ayat_case(
        self,
        left_ayat: AyatShort,
        favorite_button: types.InlineKeyboardButton,
    ) -> types.InlineKeyboardMarkup:
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=LEFT_BUTTON_TEXT_TEMPLATE.format(left_ayat.title()),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=left_ayat.id),
                ),
            )
            .row(favorite_button)
        )

    def _middle_ayat_case(
        self,
        left_ayat: AyatShort,
        right_ayat: AyatShort,
        favorite_button: types.InlineKeyboardButton,
    ) -> types.InlineKeyboardMarkup:
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=LEFT_BUTTON_TEXT_TEMPLATE.format(left_ayat.title()),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=left_ayat.id),
                ),
                types.InlineKeyboardButton(
                    text=RIGHT_BUTTON_TEXT_TEMPLATE.format(right_ayat.title()),
                    callback_data=self._pagination_buttons_keyboard.format(ayat_id=right_ayat.id),
                ),
            )
            .row(favorite_button)
        )

    def _only_one_ayat_case(self, favorite_button: types.InlineKeyboardButton):
        return (
            types.InlineKeyboardMarkup()
            .row(
                favorite_button,
            )
        )
