from repository.update_log import UpdatesLogRepositoryInterface
from services.answers.answer import TextAnswer
from services.answers.log_answer import LoggedAnswer
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
        await LoggedAnswer(
            TextAnswer(message=notification_text),
            self._udpate_log_repository,
        ).send(settings.ADMIN_CHAT_IDS[0])
