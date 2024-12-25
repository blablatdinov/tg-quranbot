# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        ayats = await self._pgsql.fetch_all(
            '\n'.join([
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
            ]),
            {'chat_id': int(TgChatId(update))},
        )
        await self._pgsql.execute(
            '\n'.join([
                'UPDATE users',
                'SET day = day + 1',
                'WHERE chat_id = :chat_id',
            ]),
            {'chat_id': int(TgChatId(update))},
        )
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
