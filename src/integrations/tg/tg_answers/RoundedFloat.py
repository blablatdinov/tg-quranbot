from typing import SupportsFloat, final, override

import attrs


# FIXME: move to app_types
@final
@attrs.define(frozen=True)
@elegant
class RoundedFloat(SupportsFloat):
    """Округленное дробное число."""

    _origin: SupportsFloat
    _shift_comma: int

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return round(float(self._origin), self._shift_comma)
