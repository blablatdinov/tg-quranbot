import json
from typing import Optional, Union

import httpx
from loguru import logger

from db.connection import database
from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface, FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats, NeighborAyatsRepositoryInterface
from repository.ayats.sura import SuraInterface
from services.answers.answer import FileAnswer, KeyboardInterface, TelegramFileIdAnswer


class SearchQueryInterface(object):
    """Интерфейс объекта с запросом для поиска."""

    def sura(self) -> int:
        """Номер суры.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def ayat(self) -> str:
        """Номер аята.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SearchQuery(SearchQueryInterface):
    """Запросом для поиска."""

    def __init__(self, query: str):
        self._query = query

    def sura(self) -> int:
        """Номер суры.

        :return: int
        """
        return int(self._query.split(':')[0])

    def ayat(self) -> str:
        """Номер аята.

        :return: str
        """
        return self._query.split(':')[1]


class ValidatedSearchQuery(SearchQueryInterface):
    """Декоратор, валидирующий запрос для поиска."""

    def __init__(self, query: SearchQueryInterface):
        self._origin = query

    def sura(self) -> int:
        """Номер суры.

        :return: int
        :raises SuraNotFoundError: if sura not found
        """
        max_sura_num = 114
        sura_num = self._origin.sura()
        if not 0 < sura_num <= max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        return sura_num

    def ayat(self) -> str:
        """Номер аята.

        :return: str
        :raises AyatNotFoundError: if ayat not found
        """
        ayat_num = self._origin.ayat()
        if ayat_num == '0' or '-' in ayat_num:
            raise AyatNotFoundError
        return ayat_num


class AyatNeighborAyatKeyboard(KeyboardInterface):

    def __init__(self, ayats_neighbors: NeighborAyatsRepositoryInterface):
        self._ayats_neighbors = ayats_neighbors

    async def generate(self, update: Update) -> str:
        left = await self._ayats_neighbors.left_neighbor()
        right = await self._ayats_neighbors.right_neighbor()
        return json.dumps({
            'inline_keyboard': [[
                {
                    'text': '<- {0}:{1}'.format(left.sura_num, left.ayat_num),
                    'callback_data': 'getAyat({0})'.format(left.id),
                },
                {
                    'text': '{0}:{1} ->'.format(right.sura_num, right.ayat_num),
                    'callback_data': 'getAyat({0})'.format(right.id),
                },
            ]],
        })


class AyatFavoriteKeyboardButton(KeyboardInterface):

    def __init__(self, ayat: Ayat, keyboard: KeyboardInterface, favorite_ayat_repo: FavoriteAyatRepositoryInterface):
        self._ayat = ayat
        self._origin = keyboard
        self._favorite_ayat_repo = favorite_ayat_repo

    async def generate(self, update: Update) -> str:
        keyboard = json.loads(await self._origin.generate(update))
        is_favor = await self._favorite_ayat_repo.check_ayat_is_favorite_for_user(self._ayat.id, update.chat_id())
        keyboard['inline_keyboard'].append([{
            'text': 'Удалить из избранного' if is_favor else 'Добавить в избранное',
            'callback_data': ('removeFromFavor({0})' if is_favor else 'addToFavor({0})').format(self._ayat.id),
        }])
        return json.dumps(keyboard)


class AyatSearchInterface(object):

    async def search(self, search_query: Union[str, int]) -> Ayat:
        raise NotImplementedError


class AyatById(AyatSearchInterface):

    def __init__(self, ayat_repo: AyatRepositoryInterface):
        self._ayat_repo = ayat_repo

    async def search(self, search_query: Union[str, int]) -> Ayat:
        return await self._ayat_repo.get(search_query)


class AyatBySuraAyatNum(AyatSearchInterface):

    def __init__(self, sura: SuraInterface):
        self._sura = sura

    async def search(self, search_query: str) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        """
        logger.info('Search ayat by {0}'.format(search_query))
        query = ValidatedSearchQuery(
            SearchQuery(search_query),
        )
        ayat_num = query.ayat()
        ayats = await self._sura.ayats(query.sura())
        print(ayats)
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

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split('-'))
        if int(ayat_num) in range(left, right + 1):
            return ayat
        return None

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split(','))
        if int(ayat_num) in range(left, right + 1):
            return ayat
        return None


class AyatBySuraAyatNumAnswer(TgAnswerInterface):
    """Ответ на поиск аята по номеру суры, аята."""

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_search: AyatSearchInterface,
    ):
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_search = ayat_search

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        """
        result_ayat = await self._ayat_search.search(update.message.text)
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(result_ayat),
                ),
                AyatFavoriteKeyboardButton(
                    result_ayat,
                    AyatNeighborAyatKeyboard(
                        NeighborAyats(database, result_ayat.id),
                    ),
                    FavoriteAyatsRepository(database),
                )
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    result_ayat.audio_telegram_id,
                ),
                TgTextAnswer(
                    self._message_answer,
                    result_ayat.link_to_audio_file,
                ),
            ),
        ).build(update)
