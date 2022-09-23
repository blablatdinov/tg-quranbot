from repository.update_log import UpdatesLogRepositoryInterface
from utlls import get_bot_instance

bot = get_bot_instance()


class MessagesDeletedEvent(object):
    """Событие удаления сообщений."""

    event_name = 'Messages.Deleted'
    _messages_repository: UpdatesLogRepositoryInterface

    def __init__(self, messages_repository: UpdatesLogRepositoryInterface):
        self._messages_repository = messages_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
