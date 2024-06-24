from typing import Protocol

from pyeo import elegant


@elegant
class NeighborAyatsButtons(Protocol):
    """Кнопки для клавиатуры с соседними аятами."""

    async def left(self) -> dict[str, str] | None:
        """Левая кнопка."""

    async def right(self) -> dict[str, str] | None:
        """Правая кнопка."""
