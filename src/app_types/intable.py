class Intable(object):
    """Интерфейс объектов, которые можно привести к числу."""

    def __int__(self) -> int:
        """Приведение к числу.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
