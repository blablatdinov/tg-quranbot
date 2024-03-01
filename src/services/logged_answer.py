"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import json
from typing import final, override

import attrs
from pyeo import elegant

from app_types.update import Update
from integrations.tg.sendable import SendableInterface
from srv.events.sink import SinkInterface


@final
@attrs.define(frozen=True)
@elegant
class LoggedAnswer(SendableInterface):
    """Декоратор логирующий сообщения."""

    _origin: SendableInterface
    _event_sink: SinkInterface

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: str
        :return: list[dict]
        """
        await self._event_sink.send(
            'updates_log',
            {
                'messages': [{
                    'message_json': json.dumps(update.asdict()['message']),
                    'is_unknown': False,
                    'trigger_message_id': None,
                }],
            },
            'Messages.Created',
            1,
        )
        sent_answers = await self._origin.send(update)
        await self._event_sink.send(
            'updates_log',
            {
                'messages': [
                    {
                        'message_json': json.dumps(answer['result']),
                        'is_unknown': False,
                        'trigger_message_id': update.asdict()['message']['message_id'],
                    }
                    for answer in sent_answers
                ],
            },
            'Messages.Created',
            1,
        )
        return sent_answers
