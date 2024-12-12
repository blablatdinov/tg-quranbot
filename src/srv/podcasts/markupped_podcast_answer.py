# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.tg_answer_markup import TgAnswerMarkup
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer
from srv.podcasts.podcast import Podcast
from srv.podcasts.podcast_keyboard import PodcastKeyboard


@final
@attrs.define(frozen=True)
class MarkuppedPodcastAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database
    _podcast: Podcast

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        chat_id = TgChatId(update)
        return await TgAnswerMarkup(
            FileAnswer(
                TelegramFileIdAnswer(
                    TgChatIdAnswer(
                        TgAudioAnswer(
                            self._origin,
                        ),
                        chat_id,
                    ),
                    self._podcast,
                ),
                TgTextAnswer.str_ctor(
                    TgChatIdAnswer(
                        TgMessageAnswer(
                            self._origin,
                        ),
                        chat_id,
                    ),
                    await self._podcast.file_link(),
                ),
                self._debug_mode,
            ),
            PodcastKeyboard(self._pgsql, self._podcast),
        ).build(update)
