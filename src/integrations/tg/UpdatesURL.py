from app_types.stringable import SupportsStr


import attrs


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class UpdatesURL(SupportsStr):
    """Базовый URL обновлений из телеграма."""

    _token: str

    @override
    def __str__(self) -> str:
        """Строчное представление.

        :return: str
        """
        return 'https://api.telegram.org/bot{0}/getUpdates'.format(self._token)