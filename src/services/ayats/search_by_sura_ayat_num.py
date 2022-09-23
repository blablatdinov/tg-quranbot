from typing import Union

import httpx
from loguru import logger

from db.connection import database
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.schemas import Ayat
from repository.ayats.sura import SuraInterface
from services.ayats.ayat_answer import AyatAnswer, AyatAnswerKeyboard
from services.ayats.search.ayat_search_query import SearchQuery, ValidatedSearchQuery


class AyatSearchInterface(object):
    """Интерфейс поиска аята."""

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatBySuraAyatNum(AyatSearchInterface):
    """Поиск аята по номеру суры, аята."""

    def __init__(self, sura: SuraInterface):
        self._sura = sura

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        :raises TypeError: if search_query type is not available
        """
        logger.info('Search ayat by {0}'.format(search_query))
        if isinstance(search_query, int):
            raise TypeError
        query = ValidatedSearchQuery(
            SearchQuery(search_query),
        )
        ayat_num = query.ayat()
        ayats = await self._sura.ayats(query.sura())
        for ayat in ayats:
            result_ayat = self._search_in_sura_ayats(ayat, ayat_num)
            if result_ayat:
                return result_ayat[0]
        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        result_ayat: tuple[Ayat, ...] = ()
        if '-' in ayat.ayat_num:
            result_ayat = self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            result_ayat = self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            result_ayat = (ayat,)
        return result_ayat

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split('-'))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split(','))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()


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
        """
        result_ayat = await self._ayat_search.search(update.message().text)
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(result_ayat, FavoriteAyatsRepository(database)),
        ).build(update)
