"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import final
from integrations.tg.tg_answers import TgChatIdAnswer, TgEmptyAnswer, TgTextAnswer
from repository.update_log import UpdatesLogRepositoryInterface
from settings import settings


class NotificationCreatedEvent(object):
    """Событие удаления сообщений."""

    event_name = 'Notification.Created'

    def __init__(self, updates_log_repository: UpdatesLogRepositoryInterface):
        """Конструктор класса.

        :param updates_log_repository: UpdatesLogRepositoryInterface
        """
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
