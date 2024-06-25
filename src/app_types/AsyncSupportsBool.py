from pyeo import elegant


from typing import Protocol


@elegant
class AsyncSupportsBool(Protocol):
    """Интерфейс объектов, которые можно привести к булевому значению."""

    async def to_bool(self) -> bool:
        """Приведение к булевому значению."""