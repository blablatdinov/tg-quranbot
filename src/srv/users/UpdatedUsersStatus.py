from pyeo import elegant


from typing import Protocol


@elegant
class UpdatedUsersStatus(Protocol):
    """Обновление статусов пользователей."""

    async def update(self, to: bool) -> None:
        """Обновление.

        :param to: bool
        """