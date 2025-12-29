# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
import uuid
from typing import Final, final, override

import attrs
import pytz
import ujson

from app_types.update import Update
from integrations.tg.sendable import Sendable
from srv.events.sink import Sink

MESSAGE_LITERAL: Final = 'message'
UPDATES_LOG: Final = 'qbot_admin.updates_log'
CALLBACK_QUERY: Final = 'callback_query'
MESSAGES: Final = 'messages'
MESSAGE_JSON: Final = 'message_json'
IS_UNKNOWN: Final = 'is_unknown'
TRIGGER_MESSAGE_ID: Final = 'trigger_message_id'
TRIGGER_CALLBACK_ID: Final = 'trigger_callback_id'
MAILING_ID: Final = 'mailing_id'
MESSAGES_CREATED: Final = 'Messages.Created'


@final
@attrs.define(frozen=True)
class LoggedAnswer(Sendable):
    """Декоратор логирующий сообщения."""

    _origin: Sendable
    _event_sink: Sink
    _mailing_id: uuid.UUID | None = None

    @override
    async def send(self, update: Update) -> list[dict]:  # noqa: WPS217, WPS231
        """Отправка.

        :param update: str
        :return: list[dict]
        """
        if update.asdict().get(MESSAGE_LITERAL):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [{
                        MESSAGE_JSON: ujson.dumps(update.asdict()[MESSAGE_LITERAL]),
                        IS_UNKNOWN: False,
                        TRIGGER_MESSAGE_ID: None,
                        TRIGGER_CALLBACK_ID: None,
                        MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                    }],
                },
                MESSAGES_CREATED,
                1,
            )
        elif update.asdict().get(CALLBACK_QUERY):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    'json': str(update),
                    'timestamp': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).isoformat(),
                },
                'Button.Pushed',
                1,
            )
        sent_answers = await self._origin.send(update)
        if update.asdict().get(MESSAGE_LITERAL):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: update.asdict()[MESSAGE_LITERAL]['message_id'],
                            TRIGGER_CALLBACK_ID: None,
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
            return sent_answers
        elif update.asdict().get(CALLBACK_QUERY):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: None,
                            TRIGGER_CALLBACK_ID: update.asdict()[CALLBACK_QUERY]['id'],
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
        else:
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: None,
                            TRIGGER_CALLBACK_ID: None,
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
        return sent_answers
