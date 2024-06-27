from app_types.update import Update
from integrations.tg.update_id import UpdateId
from services.DebugParam import DebugParam


from typing import final, override


@final
@elegant
class UpdateIdDebugParam(DebugParam):
    """Отладочная информация с идентификатором обновления."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Идентификатор обновления.

        :param update: Update
        :return: str
        """
        return 'Update id: {0}'.format(int(UpdateId(update)))