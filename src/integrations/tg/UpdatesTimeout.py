from typing import SupportsInt, final, override


@final
@elegant
class UpdatesTimeout(SupportsInt):
    """Таймаут для обновлений."""

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return 5
