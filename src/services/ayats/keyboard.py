import enum
from dataclasses import dataclass

from aiogram import types

from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.neighbor_ayats import AyatShort

KEYBOARD_AYAT_TEMPLATE = '{0}:{1}'
CALLBACK_DATA_ADD_TO_FAVORITE_TEMPLATE = 'add_to_favorite({ayat_id})'
CALLBACK_DATA_REMOVE_FROM_FAVORITE_TEMPLATE = 'remove_from_favorite({ayat_id})'


class AyatPaginatorCallbackDataTemplate(str, enum.Enum):  # noqa: WPS600
    """Шаблоны для данных в кнопках с пагинацией по аятам."""

    ayat_search_template = 'get_ayat({ayat_id})'
    favorite_ayat_template = 'get_favorite_ayat({ayat_id})'


@dataclass
class AyatSearchKeyboard(object):
    """Клавиатура, выводимая пользователям вместе с найденными аятами."""

    ayat_repository: AyatRepositoryInterface
    ayat_id: int
    ayat_is_favorite: bool
    ayat_neighbors: list[AyatShort]
    chat_id: int
    pagination_buttons_keyboard: AyatPaginatorCallbackDataTemplate

    def generate(self):
        """Генерация клавиатуры.

        :returns: InlineKeyboard
        """
        first_ayat_id = 1
        last_ayat_id = 5737
        if self.ayat_is_favorite:
            favorite_button = types.InlineKeyboardButton(
                text='Удалить из избранного',
                callback_data=CALLBACK_DATA_REMOVE_FROM_FAVORITE_TEMPLATE.format(ayat_id=self.ayat_id),
            )
        else:
            favorite_button = types.InlineKeyboardButton(
                text='Добавить в избранное',
                callback_data=CALLBACK_DATA_ADD_TO_FAVORITE_TEMPLATE.format(ayat_id=self.ayat_id),
            )

        if self.ayat_id == first_ayat_id:
            return self._first_ayat_case(self.ayat_neighbors, favorite_button)
        elif self.ayat_id == last_ayat_id:
            return self._last_ayat_case(self.ayat_neighbors, favorite_button)

        return self._middle_ayat_case(self.ayat_neighbors, favorite_button)

    def _first_ayat_case(self, neighbor_ayats, favorite_button):
        right_ayat = neighbor_ayats[1]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(right_ayat.sura_num, right_ayat.ayat_num),
                    callback_data=self.pagination_buttons_keyboard.format(ayat_id=right_ayat.id),
                ),
            )
            .row(favorite_button)
        )

    def _last_ayat_case(self, neighbor_ayats, favorite_button):
        left_ayat = neighbor_ayats[0]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(left_ayat.sura_num, left_ayat.ayat_num),
                    callback_data=self.pagination_buttons_keyboard.format(ayat_id=left_ayat.id),
                ),
            )
            .row(favorite_button)
        )

    def _middle_ayat_case(self, neighbor_ayats, favorite_button):
        left_ayat, right_ayat = neighbor_ayats[0], neighbor_ayats[2]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(left_ayat.sura_num, left_ayat.ayat_num),
                    callback_data=self.pagination_buttons_keyboard.format(ayat_id=left_ayat.id),
                ),
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(right_ayat.sura_num, right_ayat.ayat_num),
                    callback_data=self.pagination_buttons_keyboard.format(ayat_id=right_ayat.id),
                ),
            )
            .row(favorite_button)
        )
