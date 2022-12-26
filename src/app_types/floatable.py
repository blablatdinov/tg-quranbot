from typing import Protocol


class Floatable(Protocol):
    """Интерфейс числа с плавающей запятой."""

    def __float__(self):
        """Представление в форме числа с плавающей запятой."""
