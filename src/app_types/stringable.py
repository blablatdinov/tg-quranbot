class Stringable(object):
    """Интерфейс объектов, которые можно привести к строке."""

    def __str__(self) -> int:
        """Приведение к строке.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
