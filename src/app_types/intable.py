from typing import Protocol


class Intable(Protocol):
    """Интерфейс объектов, которые можно привести к числу."""

    def __int__(self) -> int:
        """Приведение к числу."""
