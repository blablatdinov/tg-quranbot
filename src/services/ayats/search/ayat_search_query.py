from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError


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
