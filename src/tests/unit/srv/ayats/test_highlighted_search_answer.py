# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT


from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.fk_text_search_query import FkTextSearchQuery
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer


async def test():
    got = await HighlightedSearchAnswer(
        FkAnswer('https://some.domain?text=How to write tests in python?'),
        FkTextSearchQuery('How to write tests'),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert got[0].url.params['text'] == '<b>How to write tests</b> in python?'


async def test_key_error():
    got = await HighlightedSearchAnswer(
        FkAnswer(),
        FkTextSearchQuery('How to write tests'),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert str(got[0].url) == 'https://some.domain'


async def test_other_text():
    got = await HighlightedSearchAnswer(
        FkAnswer('https://some.domain?text=How to write documentation'), FkTextSearchQuery('How to write tests'),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert got[0].url.params['text'] == 'How to write documentation'
