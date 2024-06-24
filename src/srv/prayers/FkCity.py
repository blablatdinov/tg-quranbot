from srv.prayers.city import City


import attrs
from pyeo import elegant


import uuid
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class FkCity(City):
    """Стаб города."""

    _city_id: uuid.UUID
    _name: str

    @override
    async def city_id(self) -> uuid.UUID:
        """Идентификатор города.

        :return: uuid.UUID
        """
        return self._city_id

    @override
    async def name(self) -> str:
        """Имя города.

        :return: name
        """
        return self._name