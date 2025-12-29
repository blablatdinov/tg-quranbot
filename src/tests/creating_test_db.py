# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from pathlib import Path

import psycopg2

from settings import BASE_DIR, Settings

settings = Settings(_env_file=BASE_DIR.parent / '.env')


def create_db() -> None:
    connection = psycopg2.connect(
        str(settings.DATABASE_URL).replace('quranbot_test', 'postgres'),
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
    qbot_connection = psycopg2.connect(str(settings.DATABASE_URL))
    qbot_connection.autocommit = True
    qbot_cursor = qbot_connection.cursor()
    apply_migrations(qbot_cursor)
    fixtures = (
        'src/tests/e2e/db-fixtures/bot/files.sql',
        'src/tests/e2e/db-fixtures/bot/suras.sql',
        'src/tests/e2e/db-fixtures/bot/ayats.sql',
        'src/tests/e2e/db-fixtures/bot/podcasts.sql',
        'src/tests/e2e/db-fixtures/bot/cities.sql',
        'src/tests/e2e/db-fixtures/bot/prayers.sql',
        'src/tests/e2e/db-fixtures/bot/admin_messages.sql',
    )
    for fixture in fixtures:
        qbot_cursor.execute(Path(fixture).read_text(encoding='utf-8'))
    qbot_connection.close()


def drop_db() -> None:
    connection = psycopg2.connect(
        str(settings.DATABASE_URL).replace('quranbot_test', 'postgres'),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('DROP DATABASE quranbot_test')
