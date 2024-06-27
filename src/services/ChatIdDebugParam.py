from app_types.update import Update
from integrations.tg.tg_chat_id import TgChatId
from services.DebugParam import DebugParam


from typing import final, override


@final
@elegant
class ChatIdDebugParam(DebugParam):
    """Отладочная информация с идентификатором чата."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Идентификатор чата.

        :param update: Update
        :return: str
        """
        return 'Chat id: {0}'.format(int(TgChatId(update)))