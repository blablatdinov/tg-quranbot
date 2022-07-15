from typing import Optional

from answerable import Answerable
from app_types.intable import Intable
from exceptions import AyatNotFoundError
from repository.ayats.ayat import Ayat
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboard import AyatPaginatorCallbackDataTemplate, AyatSearchKeyboard


# TODO: тесты
class FavoriteAyats(AyatSearchInterface):
    """Получить избранные аяты."""

    _ayat_repository: FavoriteAyatRepositoryInterface
    _chat_id: int
    _ayat_id: Optional[Intable]
    _ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate

    def __init__(
        self,
        ayat_repository: FavoriteAyatRepositoryInterface,
        chat_id: int,
        ayat_id: Optional[Intable] = None,  # TODO: maybe separate class for None cases
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

        return [ayat for ayat in favorite_ayats if ayat.id == int(self._ayat_id)][0]


class SearchAnswer(Answerable):
    """Класс, собирающий ответ на запрос о поиске."""

    _ayat_search: AyatSearchInterface

    def __init__(self, ayat_search: AyatSearchInterface, keyboard: AyatSearchKeyboard):
        self._ayat_search = ayat_search
        self._keyboard = keyboard

    async def to_answer(self) -> AnswerInterface:
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


class AyatNotFoundSafeAnswer(Answerable):
    """Декортаор, для обработки ошибки."""

    _origin: Answerable

    def __init__(self, answerable: Answerable):
        self._origin = answerable

    async def to_answer(self) -> AnswerInterface:
        """Конвертация в ответ.

        :returns: AnswerInterface
        """
        try:
            return await self._origin.to_answer()
        except AyatNotFoundError as error:
            return await error.to_answer()


class AyatFavoriteStatus(object):
    """Статус избранности аята."""

    _favorite_ayat_repository: FavoriteAyatRepositoryInterface
    _ayat_id: Intable
    _chat_id: int

    def __init__(
        self,
        favorite_ayat_repository: FavoriteAyatRepositoryInterface,
        ayat_id: Intable,
        chat_id: int,
    ):
        self._favorite_ayat_repository = favorite_ayat_repository
        self._ayat_id = ayat_id
        self._chat_id = chat_id

    async def change(self, is_favorite: bool):
        """Поменять статус.

        :param is_favorite: bool
        """
        if is_favorite:
            await self._favorite_ayat_repository.add_to_favorite(
                self._chat_id, int(self._ayat_id),
            )
        else:
            await self._favorite_ayat_repository.remove_from_favorite(
                self._chat_id, int(self._ayat_id),
            )
