class Stringable(object):
    """Интерфейс объектов, которые можно привести к строке."""

    def __str__(self) -> str:
        """Приведение к строке.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class ThroughStringable(Stringable):
    """Обертка для строки."""

    def __init__(self, source: str):
        """Конструктор класса.

        :param source: str
        """
        self._source = source

    def __str__(self):
        """Строковое представление.

        :return: str
        """
        return self._source


class UnwrappedString(Stringable):
    """Строки без переноса."""

    def __init__(self, origin: Stringable):
        """Конструктор класса.

        :param origin: str
        """
        self._origin = origin

    def __str__(self):
        """Строковое представление.

        :return: str
        """
        return str(self._origin).replace('\n', '')
