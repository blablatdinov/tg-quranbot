class Floatable(object):
    """Интерфейс числа с плавающей запятой."""

    def __float__(self):
        """Представление в форме числа с плавающей запятой.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
