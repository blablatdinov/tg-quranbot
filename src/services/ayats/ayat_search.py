from dataclasses import dataclass
from typing import Optional

from exceptions import AyatNotFoundError, SuraNotFoundError, exception_to_answer_formatter
from repository.ayats.ayat import Ayat
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.ayat import AyatServiceInterface
from services.ayats.keyboard import AyatPaginatorCallbackDataTemplate, AyatSearchKeyboard


class AyatSearchInterface(object):
    """Интерфейс класса, осуществляющего поиск аятов."""

    ayat_service: AyatServiceInterface

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class FavoriteAyats(AyatSearchInterface):
    """Получить избранные аяты."""

    ayat_service: AyatServiceInterface
    ayat_id: Optional[int] = None

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


@dataclass
class AyatById(AyatSearchInterface):
    """Аят по идентификатору."""

    ayat_service: AyatServiceInterface
    ayat_id: int

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск по идентификатору.

        :returns: Ayat
        """
        return await self.ayat_service.ayat_repository.get(self.ayat_id)


@dataclass
class AyatSearch(AyatSearchInterface):
    """Класс, обрабатывающий логику поиска аятов."""

    ayat_service: AyatServiceInterface
    search_input: str

    async def search(self) -> Ayat:
        """Поиск по номеру суры и аята.

        :returns: Ayat
        :raises AyatNotFoundError: if ayat not found
        """
        sura_num, ayat_num = self.search_input.split(':')
        ayats = await self.ayat_service.ayat_repository.get_ayats_by_sura_num(int(sura_num))
        self._validate_sura_ayat_numbers(int(sura_num), int(ayat_num))
        for ayat in ayats:
            result_ayat = self._search_in_sura_ayats(ayat, ayat_num)

            if result_ayat:
                return result_ayat

        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        result_ayat = None
        if '-' in ayat.ayat_num:
            result_ayat = self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            result_ayat = self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            result_ayat = ayat

        return result_ayat

    def _validate_sura_ayat_numbers(self, sura_num: int, ayat_num: int) -> None:
        max_sura_num = 114
        if not 0 < sura_num <= max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        if ayat_num <= 0:
            raise AyatNotFoundError

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split('-'))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return ayat
        return None

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split(','))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return ayat
        return None


@dataclass
class SearchAnswer(object):
    """Класс, собирающий ответ на запрос о поиске."""

    ayat_search: AyatSearchInterface
    neighbors_ayat_repository: NeighborAyatsRepositoryInterface

    @exception_to_answer_formatter
    async def transform(self) -> AnswerInterface:
        """Трансформировать переданные данные в ответ.

        :returns: AnswerInterface
        """
        ayat = await self.ayat_search.search()
        return AnswersList(
            Answer(
                message=str(ayat),
                keyboard=AyatSearchKeyboard(
                    ayat_repository=self.ayat_search.ayat_service.ayat_repository,
                    ayat_id=ayat.id,
                    ayat_is_favorite=(
                        await self.ayat_search.ayat_service
                        .ayat_repository
                        .check_ayat_is_favorite_for_user(
                            ayat.id, self.ayat_search.ayat_service.chat_id,
                        )
                    ),
                    ayat_neighbors=await self.neighbors_ayat_repository.get_ayat_neighbors(ayat.id),
                    chat_id=self.ayat_search.ayat_service.chat_id,
                    pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
                ).generate(),
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
