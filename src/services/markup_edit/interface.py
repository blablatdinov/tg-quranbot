from typing import Protocol


class MarkupEditInterface(Protocol):
    """Интерфейс для классов, редактирующих клавиатуру."""

    async def edit(self) -> None:
        """Редактирование."""
