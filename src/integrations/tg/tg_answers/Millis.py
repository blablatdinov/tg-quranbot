import attrs


from typing import SupportsFloat, final, override


# FIXME: move to app_types
@final
@attrs.define(frozen=True)
class Millis(SupportsFloat):
    """Миллисекунды."""

    _millis: float

    @classmethod
    def seconds_ctor(cls, seconds: float) -> SupportsFloat:
        """Конструктор для секунд.

        :param seconds: float
        :return: Millis
        """
        return Millis(seconds * 1000)

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return self._millis