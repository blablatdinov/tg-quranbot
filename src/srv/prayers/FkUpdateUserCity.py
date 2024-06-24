from srv.prayers.updated_user_city import UpdatedUserCity


import attrs
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class FkUpdateUserCity(UpdatedUserCity):
    """Стаб для обновления города."""

    @override
    async def update(self) -> None:
        """Обновление."""