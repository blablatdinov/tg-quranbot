from app_types.stringable import SupportsStr
from integrations.tg.UpdatesURLInterface import UpdatesURLInterface


import attrs


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class UpdatesWithOffsetURL(UpdatesURLInterface):
    """URL для получения только новых обновлений."""

    _updates_url: SupportsStr

    @override
    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        :return: str
        """
        return '{0}?offset={1}'.format(self._updates_url, update_id)