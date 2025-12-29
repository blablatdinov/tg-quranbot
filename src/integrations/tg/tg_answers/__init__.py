# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import override

from integrations.tg.tg_answers.answer_fork import TgAnswerFork
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.callback_query_regex_answer import TgCallbackQueryRegexAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.delete_message_answer import TgMessageDeleteAnswer
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from integrations.tg.tg_answers.html_parse_answer import TgHtmlParseAnswer
from integrations.tg.tg_answers.link_preview_options import TgLinkPreviewOptions
from integrations.tg.tg_answers.measure_answer import TgMeasureAnswer
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from integrations.tg.tg_answers.message_keyboard_edit_answer import TgKeyboardEditAnswer
from integrations.tg.tg_answers.message_regex_answer import TgMessageRegexAnswer
from integrations.tg.tg_answers.reply_source_answer import TgReplySourceAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_answers.tg_answer_markup import TgAnswerMarkup
