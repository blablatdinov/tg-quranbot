from typing import Protocol

from pyeo import elegant


@elegant
class UpdatedUsersStatus(Protocol):
    """Обновление статусов пользователей."""

    async def update(self, to: bool) -> None:
        """Обновление.

        :param to: bool
        """
