from typing import SupportsInt, final, override

import attrs
import httpx

from integrations.tg.UpdatesURLInterface import UpdatesURLInterface


@final
@attrs.define(frozen=True)
@elegant
class UpdatesLongPollingURL(UpdatesURLInterface):
    """URL обновлений с таймаутом."""

    _origin: UpdatesURLInterface
    _long_polling_timeout: SupportsInt

    @override
    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        :return: str
        """
        return str(httpx.URL(self._origin.generate(update_id)).copy_add_param(
            'timeout',
            int(self._long_polling_timeout),
        ))
