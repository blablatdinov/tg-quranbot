from typing import Protocol

from app_types.stringable import Stringable


class KeyboardInterface(Protocol):
    """Интерфейс клавиатуры."""

    async def generate(self, update: Stringable) -> str:
        """Генерация.

        :param update: Stringable
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
