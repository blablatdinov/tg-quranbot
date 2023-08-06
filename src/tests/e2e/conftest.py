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
import multiprocessing
from pathlib import Path

import pytest
from telethon.sync import TelegramClient
import psycopg

from main import main
from settings import settings


def generate_fixture(dump_path: Path):
    @pytest.fixture(scope='module')
    def my_fixture():  # noqa: WPS430
        qbot_connection = psycopg.connect(
            'postgres://almazilaletdinov@localhost:5432/quranbot_test',
        )
        qbot_cursor = qbot_connection.cursor()
        qbot_cursor.execute(dump_path.read_text())
    return my_fixture


def inject_fixture(dump_name):
    globals()['{0}_dump'.format(dump_name)] = generate_fixture(
        Path(__file__).parent / 'fixtures' / '{0}.sql'.format(dump_name),
    )  # noqa: WPS421


# inject_fixture('start_dump')
# inject_fixture('my_admin', 200)


@pytest.fixture(scope='session')
def bot_name():
    return '@WokeUpSmiled_bot'


@pytest.fixture(scope='session')
def bot_process():
    bot = multiprocessing.Process(target=main, args=(['src/main.py', 'run_polling'],))
    bot.start()
    yield
    bot.terminate()


@pytest.fixture(scope='session')
def tg_client(bot_name):
    conn = psycopg.connect(
        'postgres://almazilaletdinov@localhost:5432/postgres',
    )
    conn.autocommit = True
    cursor = conn.cursor()
    # cursor.execute('DROP DATABASE quranbot_test')
    # cursor.execute('CREATE DATABASE quranbot_test')
    qbot_connection = psycopg.connect(
        'postgres://almazilaletdinov@localhost:5432/quranbot_test',
    )
    qbot_cursor = qbot_connection.cursor()
    qbot_cursor.execute((Path(__file__).parent / 'fixtures' / 'db_schema.sql').read_text())
    with TelegramClient('me', settings.TELEGRAM_CLIENT_ID, settings.TELEGRAM_CLIENT_HASH) as client:
        all_messages = [message.id for message in client.iter_messages('@WokeUpSmiled_bot')]
        client.delete_messages(entity=bot_name, message_ids=all_messages)
        yield client
    qbot_connection.close()
    # cursor.execute('DROP DATABASE quranbot_test')
    conn.close()
