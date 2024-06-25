from typing import Protocol

from pyeo import elegant


@elegant
class AsyncSupportsBool(Protocol):
    """Интерфейс объектов, которые можно привести к булевому значению."""

    async def to_bool(self) -> bool:
        """Приведение к булевому значению."""
