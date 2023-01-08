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
from utlls import get_bot_instance

from repository.update_log import UpdatesLogRepositoryInterface

bot = get_bot_instance()


class MessagesDeletedEvent(object):
    """Событие удаления сообщений."""

    event_name = 'Messages.Deleted'
    _messages_repository: UpdatesLogRepositoryInterface

    def __init__(self, messages_repository: UpdatesLogRepositoryInterface):
        """Конструктор класса.

        :param messages_repository: UpdatesLogRepositoryInterface
        """
        self._messages_repository = messages_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
