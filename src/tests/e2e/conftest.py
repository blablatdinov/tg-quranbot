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

import psycopg2
import pytest
from telethon.sync import TelegramClient

from main import main
from settings import EnvFileSettings


@pytest.fixture(scope='session')
def bot_name():
    return '@WokeUpSmiled_bot'


def create_db():
    connection = psycopg2.connect('postgres://almazilaletdinov@localhost:5432/postgres')
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE DATABASE quranbot_test')
    except psycopg2.errors.DuplicateDatabase:
        drop_db()
        cursor.execute('CREATE DATABASE quranbot_test')
    qbot_connection = psycopg2.connect('postgres://almazilaletdinov@localhost:5432/quranbot_test')
    qbot_connection.autocommit = True
    qbot_cursor = qbot_connection.cursor()
    qbot_cursor.execute(Path('migrations/20230815_01_7ALQG.sql').read_text())
    fixtures = (
        'src/tests/e2e/db-fixtures/files.sql',
        'src/tests/e2e/db-fixtures/suras.sql',
        'src/tests/e2e/db-fixtures/ayats.sql',
        'src/tests/e2e/db-fixtures/podcasts.sql',
        'src/tests/e2e/db-fixtures/prayer_days.sql',
        'src/tests/e2e/db-fixtures/cities.sql',
        'src/tests/e2e/db-fixtures/prayers.sql',
        'src/tests/e2e/db-fixtures/admin_messages.sql',
    )
    for fixture in fixtures:
        print('load {0}'.format(fixture))
        qbot_cursor.execute(Path(fixture).read_text())
        print('{0} loaded'.format(fixture))


def drop_db():
    connection = psycopg2.connect('postgres://almazilaletdinov@localhost:5432/postgres')
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('DROP DATABASE quranbot_test')


@pytest.fixture()
def clear_db():
    qbot_connection = psycopg2.connect('postgres://almazilaletdinov@localhost:5432/quranbot_test')
    qbot_connection.autocommit = True
    cursor = qbot_connection.cursor()
    tables = (
        'prayers_at_user',
        'favorite_ayats',
        'users',
    )
    for table in tables:
        cursor.execute('DELETE FROM {0}'.format(table))


@pytest.fixture(scope='session')
def bot_process():
    bot = multiprocessing.Process(target=main, args=(['src/main.py', 'run_polling'],))
    bot.start()
    create_db()
    yield
    bot.terminate()
    drop_db()


@pytest.fixture()
def tg_client(bot_name):
    settings = EnvFileSettings.from_filename('../.env')
    with TelegramClient('me', settings.TELEGRAM_CLIENT_ID, settings.TELEGRAM_CLIENT_HASH) as client:
        all_messages = [message.id for message in client.iter_messages('@WokeUpSmiled_bot')]
        client.delete_messages(entity=bot_name, message_ids=all_messages)
        yield client
