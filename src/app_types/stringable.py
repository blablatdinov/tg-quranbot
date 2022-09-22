class Stringable(object):
    """Интерфейс объектов, которые можно привести к строке."""

    def __str__(self) -> str:
        """Приведение к строке.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
