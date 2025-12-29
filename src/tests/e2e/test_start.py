# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest
import ujson
from eljson.json_doc import JsonDoc


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_start(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    last_messages = wait_until(tg_client, 3)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/start.txt').read_text(encoding='utf-8')
    assert last_messages[0].message == Path('src/tests/e2e/fixtures/1_1_ayat.txt').read_text(encoding='utf-8')


@pytest.mark.usefixtures('_bot_process', '_clear_db')
@pytest.mark.flaky(retries=3)
def test_generated_events(tg_client, bot_name, wait_event):
    tg_client.send_message(bot_name, '/start')
    events = wait_event(2, delay=5)

    assert not JsonDoc(events[0]).path('$.data.messages[0].is_unknown')[0]
    assert not JsonDoc(events[1]).path('$.data.messages[0].is_unknown')[0]
    assert ujson.loads(
        JsonDoc(events[0]).path('$.data.messages[0].message_json')[0],
    )['text'] == '/start'
    assert (
        JsonDoc(events[1]).path('$.data.messages[0].trigger_message_id')[0]
        == ujson.loads(
            JsonDoc(events[0]).path('$.data.messages[0].message_json')[0],
        )['message_id']
    )
    assert (
        JsonDoc(events[1]).path('$.data.messages[1].trigger_message_id')[0]
        == ujson.loads(
            JsonDoc(events[0]).path('$.data.messages[0].message_json')[0],
        )['message_id']
    )
