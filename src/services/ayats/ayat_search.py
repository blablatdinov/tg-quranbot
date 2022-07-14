from typing import Optional

from app_types.intable import Intable
from exceptions import exception_to_answer_formatter
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboard import AyatPaginatorCallbackDataTemplate, AyatSearchKeyboard


class FavoriteAyats(AyatSearchInterface):
    """Получить избранные аяты."""

    _ayat_repository: AyatRepositoryInterface
    _chat_id: int
    _ayat_id: Optional[int]
    _ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate

    def __init__(
        self,
        ayat_repository: AyatRepositoryInterface,
        chat_id: int,
        ayat_id: Optional[int] = None,
        ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate = None,
    ):
        self._ayat_repository = ayat_repository
        self._chat_id = chat_id
        self._ayat_id = ayat_id
        if not ayat_paginator_callback_data_template:
            ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.favorite_ayat_template
        self._ayat_paginator_callback_data_template = ayat_paginator_callback_data_template

    async def search(self) -> Ayat:
        """Поиск избранных аятов.

        :returns: Ayat
        """
        favorite_ayats = await self._ayat_repository.get_favorites(self._chat_id)
        if not self._ayat_id:
            return favorite_ayats[0]

        return list(
            filter(
                lambda ayat: ayat.id == self._ayat_id,
                favorite_ayats,
            ),
        )[0]


class SearchAnswer(object):
    """Класс, собирающий ответ на запрос о поиске."""

    _ayat_search: AyatSearchInterface

    def __init__(self, ayat_search: AyatSearchInterface, keyboard: AyatSearchKeyboard):
        self._ayat_search = ayat_search
        self._keyboard = keyboard

    @exception_to_answer_formatter
    async def transform(self) -> AnswerInterface:
        """Трансформировать переданные данные в ответ.

        :returns: AnswerInterface
        """
        ayat = await self._ayat_search.search()
        return AnswersList(
            Answer(
                message=str(ayat),
                keyboard=await self._keyboard.generate(),
            ),
            Answer(link_to_file=ayat.link_to_audio_file, telegram_file_id=ayat.audio_telegram_id),
        )


class AyatFavoriteStatus(object):
    """Статус избранности аята."""

    _ayat_repository: AyatRepositoryInterface
    _ayat_id: Intable
    _chat_id: int

    def __init__(
        self,
        ayat_repository: AyatRepositoryInterface,
        ayat_id: Intable,
        chat_id: int,
    ):
        self._ayat_repository = ayat_repository
        self._ayat_id = ayat_id
        self._chat_id = chat_id

    async def change(self, is_favorite: bool):
        """Поменять статус.

        :param is_favorite: bool
        """
        if is_favorite:
            await self._ayat_repository.add_to_favorite(
                self._chat_id, int(self._ayat_id),
            )
        else:
            await self._ayat_repository.remove_from_favorite(
                self._chat_id, int(self._ayat_id),
            )
