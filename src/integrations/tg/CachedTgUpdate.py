from app_types.update import Update


import attrs
from pyeo import elegant


from typing import ClassVar, final, override


@final
@attrs.define()
@elegant
class CachedTgUpdate(Update):
    """Декоратор, для избежания повторной десериализации.

    _origin: Update - оригинальный объект обновления
    """

    _origin: Update
    _cache: ClassVar = {
        'str': None,
        'parsed': None,
        'asdict': None,
    }

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        str_cache_key = 'str'
        if not self._cache[str_cache_key]:
            self._cache[str_cache_key] = str(self._origin)
        return self._cache[str_cache_key]

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        dict_cache_key = 'asdict'
        if not self._cache[dict_cache_key]:
            self._cache[dict_cache_key] = self._origin.asdict()
        return self._cache[dict_cache_key]