import datetime
import uuid

from databases import Database

import asyncio


class SuraMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        await self._new_db.execute('DELETE FROM suras')
        rows = await self._old_db.fetch_all('SELECT id, link FROM content_sura')
        await self._new_db.execute_many('INSERT INTO suras (sura_id, link) VALUES (:sura_id, :link)', [
        {'sura_id': row._mapping['id'], 'link': row._mapping['link']}
            for row in rows
        ])


class FilesMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        await self._new_db.execute('DELETE FROM files')
        rows = await self._old_db.fetch_all('SELECT uuid, tg_file_id, link_to_file FROM content_file')
        await self._new_db.execute_many('INSERT INTO files (file_id, telegram_file_id, link, created_at) VALUES (:file_id, :telegram_file_id, :link, :created_at)', [
            {'file_id': str(row._mapping['uuid']), 'telegram_file_id': row._mapping['tg_file_id'], 'link': row._mapping['link_to_file'], 'created_at': datetime.datetime.today()}
            for row in rows
        ])


class PodcastMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        await self._new_db.execute('DELETE FROM ayats')
        rows = await self._old_db.fetch_all("""
            SELECT cf.uuid as file_id, article_link FROM content_podcast cp
            INNER JOIN content_file cf on cf.id = cp.audio_id
        """)
        await self._new_db.execute_many("""
            INSERT INTO podcasts
            (podcast_id, file_id, article_link)
            VALUES
            (:podcast_id, :file_id, :article_link)
        """, [
            {
                'podcast_id': str(uuid.uuid4()),
                'file_id': str(row._mapping['file_id']),
                'article_link': row._mapping['article_link'],
            }
            for row in rows
        ])


class AyatsMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        await self._new_db.execute('DELETE FROM ayats')
        rows = await self._old_db.fetch_all("""
            SELECT ca.id, cm.day, sura_id, cf.uuid as audio_id, ayat, content, arab_text, trans FROM content_ayat ca
            INNER JOIN content_file cf on cf.id = ca.audio_id
            INNER JOIN content_morningcontent cm on ca.one_day_content_id = cm.id
        """)
        await self._new_db.execute_many("""
            INSERT INTO ayats
            (ayat_id, public_id, day, sura_id, audio_id, ayat_number, content, arab_text, transliteration)
            VALUES
            (:ayat_id, :public_id, :day, :sura_id, :audio_id, :ayat_number, :content, :arab_text, :transliteration)
        """, [
            {
                'ayat_id': int(row._mapping['id']),
                'public_id': str(uuid.uuid4()),
                'day': int(row._mapping['day']),
                'sura_id': int(row._mapping['sura_id']),
                'audio_id': str(row._mapping['audio_id']),
                'ayat_number': row._mapping['ayat'],
                'content': row._mapping['content'],
                'arab_text': row._mapping['arab_text'],
                'transliteration': row._mapping['trans'],
            }
            for row in rows
        ])


class AdminMessagesMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        await self._new_db.execute('DELETE FROM admin_messages')
        rows = await self._old_db.fetch_all("""
            SELECT key, text FROM bot_init_adminmessage am
        """)
        await self._new_db.execute_many("""
            INSERT INTO admin_messages
            (key, text)
            VALUES
            (:key, :text)
        """, [
            {
                'key': str(row._mapping['key']),
                'text': str(row._mapping['text']),
            }
            for row in rows
        ])


class CitiesMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        # await self._new_db.execute('DELETE FROM cities')
        rows = await self._old_db.fetch_all("""
            SELECT name FROM prayer_city
        """)
        await self._new_db.execute_many("""
            INSERT INTO cities
            (city_id, name)
            VALUES
            (:city_id, :name)
        """, [
            {
                'city_id': str(uuid.uuid4()),
                'name': row._mapping['name'],
            }
            for row in rows
        ])


async def migration():
    old_db = Database('postgres://almazilaletdinov@localhost:5432/qbot')
    await old_db.connect()
    new_db = Database('postgres://almazilaletdinov@localhost:5432/qbot_aiogram')
    await new_db.connect()
    migrations = [
        # SuraMigration(old_db, new_db),
        # FilesMigration(old_db, new_db),
        # AyatsMigration(old_db, new_db),
        # PodcastMigration(old_db, new_db),
        # AdminMessagesMigration(old_db, new_db),
        # CitiesMigration(old_db, new_db),
    ]
    for migration in migrations:
        await migration.run()


asyncio.run(migration())
