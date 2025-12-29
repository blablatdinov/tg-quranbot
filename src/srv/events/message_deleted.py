# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database
from eljson.json import Json

from app_types.fk_update import FkUpdate
from app_types.logger import LogSink
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer, TgMessageDeleteAnswer, TgMessageIdAnswer
from srv.events.recieved_event import ReceivedEvent
from srv.events.sink import Sink


@final
@attrs.define(frozen=True)
class MessageDeleted(ReceivedEvent):
    """Удаление сообщения."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _events_sink: Sink
    _logger: LogSink

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработка события.

        :param json_doc: Json
        """
        await SendableAnswer(
            TgMessageIdAnswer(
                TgChatIdAnswer(
                    TgMessageDeleteAnswer(self._empty_answer),
                    json_doc.path('$.data.chat_id')[0],
                ),
                json_doc.path('$.data.message_id')[0],
            ),
            self._logger,
        ).send(FkUpdate.empty_ctor())
