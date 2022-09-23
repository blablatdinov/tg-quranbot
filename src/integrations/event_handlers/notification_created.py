from integrations.tg.tg_answers import TgChatIdAnswer, TgEmptyAnswer, TgTextAnswer
from repository.update_log import UpdatesLogRepositoryInterface
from settings import settings


class NotificationCreatedEvent(object):
    """Событие удаления сообщений."""

    event_name = 'Notification.Created'

    def __init__(self, updates_log_repository: UpdatesLogRepositoryInterface):
        self._udpate_log_repository = updates_log_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        """
        notification_text = 'Уведомление: {0}'.format(event['text'])
        TgTextAnswer(
            TgChatIdAnswer(
                TgEmptyAnswer(settings.API_TOKEN),
                settings.ADMIN_CHAT_IDS[0],
            ),
            notification_text,
        )
