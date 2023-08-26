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
from pathlib import Path

import psycopg2

from settings import EnvFileSettings


def create_db() -> None:
    connection = psycopg2.connect(
        EnvFileSettings.from_filename('../.env').DATABASE_URL.replace('quranbot_test', 'postgres'),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE DATABASE quranbot_test')
    except psycopg2.errors.DuplicateDatabase:
        drop_db()
        cursor.execute('CREATE DATABASE quranbot_test')
    connection.close()


def apply_migrations(cursor) -> None:
    migrations = sorted(
        [
            path
            for path in Path('migrations').iterdir()
            if path.name.endswith('.sql') and not path.name.endswith('rollback.sql')
        ],
        key=lambda file_path: file_path.name,
    )
    for migration in migrations:
        cursor.execute(migration.read_text())


def fill_test_db() -> None:
    qbot_connection = psycopg2.connect(EnvFileSettings.from_filename('../.env').DATABASE_URL)
    qbot_connection.autocommit = True
    qbot_cursor = qbot_connection.cursor()
    apply_migrations(qbot_cursor)
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
        qbot_cursor.execute(Path(fixture).read_text())
    qbot_connection.close()


def drop_db() -> None:
    connection = psycopg2.connect(
        EnvFileSettings.from_filename('../.env').DATABASE_URL.replace('quranbot_test', 'postgres'),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('DROP DATABASE quranbot_test')
