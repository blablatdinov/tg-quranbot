from pyeo import elegant


from typing import Protocol


@elegant
class AsyncSupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    async def to_str(self) -> str:
        """Приведение к строке."""