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
from typing import override

from integrations.tg.tg_answers.answer_fork import TgAnswerFork
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.callback_query_regex_answer import TgCallbackQueryRegexAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.delete_message_answer import TgMessageDeleteAnswer
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from integrations.tg.tg_answers.html_parse_answer import TgHtmlParseAnswer
from integrations.tg.tg_answers.interface import FkAnswer, TgAnswer
from integrations.tg.tg_answers.link_preview_options import TgLinkPreviewOptions
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.measure_answer import TgMeasureAnswer
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from integrations.tg.tg_answers.message_keyboard_edit_answer import TgKeyboardEditAnswer
from integrations.tg.tg_answers.message_regex_answer import TgMessageRegexAnswer
from integrations.tg.tg_answers.reply_source_answer import TgReplySourceAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
