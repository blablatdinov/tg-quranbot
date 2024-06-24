from app_types.stringable import AsyncSupportsStr
from exceptions.content_exceptions import CityNotSupportedError


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class CityIdByName(AsyncSupportsStr):
    """Идентификатор города по имени."""

    _name: AsyncSupportsStr
    _pgsql: Database

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        :raises CityNotSupportedError: city not found
        """
        query = 'SELECT city_id FROM cities WHERE name = :name'
        city_id = await self._pgsql.fetch_val(
            query,
            {'name': await self._name.to_str()},
        )
        if not city_id:
            raise CityNotSupportedError
        return city_id