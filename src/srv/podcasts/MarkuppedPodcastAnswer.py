from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer
from srv.podcasts.podcast import Podcast
from srv.podcasts.podcast_keyboard import PodcastKeyboard


@final
@attrs.define(frozen=True)
@elegant
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
                self._debug_mode,
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
            ),
            PodcastKeyboard(self._pgsql, self._podcast),
        ).build(update)
