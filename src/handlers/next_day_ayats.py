# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from jinja2 import Template

from app_types.update import Update
from integrations.tg.fk_keyboard import FkKeyboard
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgHtmlParseAnswer, TgTextAnswer
from integrations.tg.tg_answers.link_preview_options import TgLinkPreviewOptions
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_chat_id import TgChatId


@final
@attrs.define(frozen=True)
class NextDayAyats(TgAnswer):
    """Аяты для следующего дня."""

    _empty_answer: TgAnswer
    _pgsql: AsyncEngine

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text('\n'.join([
                'SELECT',
                '  a.sura_id,',
                '  a.ayat_number,',
                '  a.content,',
                '  s.link AS sura_link',
                'FROM public.ayats AS a',
                'JOIN public.users AS u ON a.day = u.day',
                'JOIN suras AS s ON a.sura_id = s.sura_id',
                'WHERE u.chat_id = :chat_id',
                'ORDER BY a.ayat_id',
            ])), {'chat_id': int(TgChatId(update))})
            ayats = [dict(row) for row in query_result.fetchall()]
            await conn.execute(text('\n'.join([
                'UPDATE users',
                'SET day = day + 1',
                'WHERE chat_id = :chat_id',
            ])), {'chat_id': int(TgChatId(update))})
            await conn.commit()
        return await TgLinkPreviewOptions(
            TgHtmlParseAnswer(
                TgAnswerMarkup(
                    TgTextAnswer.str_ctor(
                        TgAnswerToSender(
                            TgMessageAnswer(self._empty_answer),
                        ),
                        Template(''.join([
                            '{% for ayat in ayats %}',
                            '<b>{{ ayat.sura_id }}:{{ ayat.ayat_number }})</b> {{ ayat.content }}\n',
                            '{% endfor %}',
                            '\nhttps://umma.ru{{ sura_link }}',
                        ])).render({
                            'ayats': [
                                {
                                    'sura_id': ayat['sura_id'],
                                    'ayat_number': ayat['ayat_number'],
                                    'content': ayat['content'],
                                }
                                for ayat in ayats
                            ],
                            'sura_link': ayats[0]['sura_link'],
                        }),
                    ),
                    FkKeyboard(
                        '{"inline_keyboard":[[{"text":"Следующий день","callback_data":"nextDayAyats"}]]}',
                    ),
                ),
            ),
            disabled=True,
        ).build(update)
