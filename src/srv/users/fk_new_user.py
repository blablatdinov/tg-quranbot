from typing import final, override

import attrs
from pyeo import elegant

from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
@elegant
class FkNewUser(NewUser):
    """Фейк нового пользователя."""

    @override
    async def create(self) -> None:
        """Создание."""
