from app_types.async_int_or_none import AsyncIntOrNone


from typing import Protocol


class NewUser(Protocol):
    """Registration of user."""

    async def create(self, referrer_chat_id: AsyncIntOrNone) -> None:
        """Creation.

        :param referrer_chat_id: AsyncIntOrNone
        """