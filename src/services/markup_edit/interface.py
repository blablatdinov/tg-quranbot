class MarkupEditInterface(object):
    """Интерфейс для классов, редактирующих клавиатуру."""

    async def edit(self) -> None:
        """Редактирование.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
