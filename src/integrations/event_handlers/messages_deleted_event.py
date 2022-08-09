from loguru import logger

from exceptions import MessageToDeleteNotFound
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
        """
        messages = await self._messages_repository.get_messages(event['message_ids'])
        for message in messages:
            try:
                await bot.delete_message(message.chat_id, message.message_id)
            except MessageToDeleteNotFound:
                logger.warning('Message with id={0} chat_id={1} not found for deleting'.format(
                    message.message_id, message.chat_id,
                ))
