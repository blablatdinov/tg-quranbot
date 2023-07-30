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
from pyeo import elegant
from typing import final

import attrs
import httpx

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from repository.podcast import RandomPodcastInterface
from services.answers.answer import FileAnswer, TelegramFileIdAnswer


@final
@attrs.define(frozen=True)
@elegant
class PodcastAnswer(TgAnswerInterface):
    """Ответ с подкастом."""

    _debug_mode: bool
    _origin: TgAnswerInterface
    _podcast: RandomPodcastInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        chat_id = int(TgChatId(update))
        return await FileAnswer(
            self._debug_mode,
            TelegramFileIdAnswer(
                TgChatIdAnswer(
                    TgAudioAnswer(
                        self._origin,
                    ),
                    chat_id,
                ),
                await self._podcast.audio_telegram_id(),
            ),
            TgTextAnswer(
                TgChatIdAnswer(
                    TgMessageAnswer(
                        self._origin,
                    ),
                    chat_id,
                ),
                await self._podcast.link_to_audio_file(),
            ),
        ).build(update)
