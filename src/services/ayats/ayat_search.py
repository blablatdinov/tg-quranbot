from dataclasses import dataclass
from typing import Optional

from exceptions import exception_to_answer_formatter
from repository.ayats.ayat import Ayat
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.ayat import AyatServiceInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboard import AyatPaginatorCallbackDataTemplate, AyatSearchKeyboard


@dataclass
class FavoriteAyats(AyatSearchInterface):
    """Получить избранные аяты."""

    ayat_service: AyatServiceInterface
    ayat_id: Optional[int] = None
    ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.favorite_ayat_template

    async def search(self) -> Ayat:
        """Поиск избранных аятов.

        :returns: Ayat
        """
        favorite_ayats = await self.ayat_service.ayat_repository.get_favorites(self.ayat_service.chat_id)
        if not self.ayat_id:
            return favorite_ayats[0]

        return list(
            filter(
                lambda ayat: ayat.id == self.ayat_id,
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


@dataclass
class AyatFavoriteStatus(object):
    """Статус избранности аята."""

    ayat_service: AyatServiceInterface
    ayat_id: int
    neighbors_ayat_repository: NeighborAyatsRepositoryInterface

    async def generate_refreshed_keyboard(self) -> AyatSearchKeyboard:
        """Сгенерировать обновленную клавиатуру.

        :returns: AyatSearchKeyboard
        """
        return AyatSearchKeyboard(
            ayat_repository=self.ayat_service.ayat_repository,
            ayat_id=self.ayat_id,
            ayat_is_favorite=(
                await self.ayat_service
                .ayat_repository
                .check_ayat_is_favorite_for_user(self.ayat_id, self.ayat_service.chat_id)
            ),
            ayat_neighbors=await self.neighbors_ayat_repository.get_ayat_neighbors(self.ayat_id),
            chat_id=self.ayat_service.chat_id,
            pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ).generate()

    async def change(self, is_favorite: bool):
        """Поменять статус.

        :param is_favorite: bool
        """
        if is_favorite:
            await self.ayat_service.ayat_repository.add_to_favorite(
                self.ayat_service.chat_id, self.ayat_id,
            )
        else:
            await self.ayat_service.ayat_repository.remove_from_favorite(
                self.ayat_service.chat_id, self.ayat_id,
            )
