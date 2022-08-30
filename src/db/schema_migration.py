import asyncio
import datetime
import uuid

from databases import Database


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
        await self._new_db.execute('DELETE FROM cities')
        rows = await self._old_db.fetch_all("""
            SELECT name, uuid FROM prayer_city
        """)
        await self._new_db.execute_many("""
            INSERT INTO cities
            (city_id, name)
            VALUES
            (:city_id, :name)
        """, [
            {
                'city_id': str(row._mapping['uuid']),
                'name': row._mapping['name'],
            }
            for row in rows
        ])


class PrayerDayMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        rows = await self._old_db.fetch_all("""
            SELECT date FROM prayer_day
        """)
        await self._new_db.execute_many("""
            INSERT INTO prayer_days
            (date)
            VALUES
            (:date)
        """, [
            {
                'date': row._mapping['date'],
            }
            for row in rows
        ])


class PrayerMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        rows = await self._old_db.fetch_all("""
            SELECT pp.id, pp.name, time, pc.uuid as city_id, pd.date FROM prayer_prayer pp 
            INNER JOIN prayer_city pc on pc.id = pp.city_id
            INNER JOIN prayer_day pd on pp.day_id = pd.id
        """)
        await self._new_db.execute_many("""
            INSERT INTO prayers
            (prayer_id, name, time, city_id, day_id)
            VALUES
            (:prayer_id, :name, :time, :city_id, :day_id)
        """, [
            {
                'prayer_id': row._mapping['id'],
                'name': row._mapping['name'],
                'time': row._mapping['time'],
                'city_id': str(row._mapping['city_id']),
                'day_id': row._mapping['date'],
            }
            for row in rows
        ])


class PrayerAtUserGroupMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        rows = await self._old_db.fetch_all('SELECT uuid FROM prayer_prayeratusergroup')
        await self._new_db.execute_many("""
            INSERT INTO prayers_at_user_groups (prayers_at_user_group_id) VALUES (:id)
        """, [
            {
                'id': str(row._mapping['uuid']),
            }
            for row in rows
        ])


class PrayerAtUserMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        rows = await self._old_db.fetch_all("""
            SELECT
                pp.id,
                bis.tg_chat_id as user_id,
                pp.prayer_id,
                pp.is_read,
                pau.uuid 
            FROM prayer_prayeratuser pp
            INNER JOIN bot_init_subscriber bis on bis.id = pp.subscriber_id
            INNER JOIN prayer_prayeratusergroup pau on pau.id = pp.prayer_group_id
        """)
        await self._new_db.execute_many("""
            INSERT INTO prayers_at_user
            (prayer_at_user_id, public_id, user_id, prayer_id, is_read, prayer_group_id)
            VALUES
            (:prayer_at_user_id, :public_id, :user_id, :prayer_id, :is_read, :prayer_group_id)
        """, [
            {
                'prayer_at_user_id': row._mapping['id'],
                'public_id': str(uuid.uuid4()),
                'user_id': row._mapping['user_id'],
                'prayer_id': row._mapping['prayer_id'],
                'is_read': row._mapping['is_read'],
                'prayer_group_id': str(row._mapping['uuid']),
            }
            for row in rows
        ])


class UsersMigration(object):

    def __init__(self, old_db, new_db):
        self._old_db = old_db
        self._new_db = new_db

    async def run(self):
        rows = await self._old_db.fetch_all("""
            SELECT
                bis.id,
                bis.tg_chat_id,
                bis.is_active,
                bis.day,
                pc.uuid as city_id,
                r.tg_chat_id as referrer_id
            FROM bot_init_subscriber bis
            LEFT JOIN prayer_city pc on pc.id = bis.city_id
            LEFT JOIN bot_init_subscriber r on bis.referer_id = r.id
            ORDER BY r.id DESC
        """)
        await self._new_db.execute_many("""
            INSERT INTO users
            (chat_id, is_active, comment, day, city_id, legacy_id)
            VALUES
            (:chat_id, :is_active, :comment, :day, :city_id, :legacy_id)
        """, [
            {
                'legacy_id': row._mapping['id'],
                'chat_id': row._mapping['tg_chat_id'],
                'is_active': row._mapping['is_active'],
                'day': row._mapping['day'],
                'city_id': str(row._mapping['city_id']) if row._mapping['city_id'] else None,
            }
            for row in rows
        ])
        for row in rows:
            await self._new_db.execute(
                'UPDATE users SET referrer_id = :referrer_id WHERE chat_id = :chat_id',
                {'referrer_id': row._mapping['referrer_id'], 'chat_id': row._mapping['tg_chat_id']},
            )


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
        # PrayerDayMigration(old_db, new_db),
        # PrayerMigration(old_db, new_db),
        # PrayerAtUserGroupMigration(old_db, new_db),
        UsersMigration(old_db, new_db),
        PrayerAtUserMigration(old_db, new_db),
    ]
    for migration in migrations:
        await migration.run()


asyncio.run(migration())
