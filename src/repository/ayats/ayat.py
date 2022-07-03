from pydantic import BaseModel


class Ayat(BaseModel):
    """Модель аята."""

    id: int
    sura_num: int
    ayat_num: str
    arab_text: str
    content: str  # noqa: WPS110 wrong variable name
    transliteration: str
    sura_link: str
    audio_telegram_id: str
    link_to_audio_file: str

    def __str__(self) -> str:
        """Отформатировать аят для сообщения.

        :returns: str
        """
        link = 'https://umma.ru{sura_link}'.format(sura_link=self.sura_link)
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=link,
            sura=self.sura_num,
            ayat=self.ayat_num,
            arab_text=self.arab_text,
            content=self.content,
            transliteration=self.transliteration,
        )


class AyatRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Метод для получения первого аята.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_ayat_by_sura_ayat_num(self, sura_num: str, ayat_num: str) -> Ayat:
        """Получить аят по номеру суры и аята.

        :param sura_num: int
        :param ayat_num: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Проверить входит ли аят в избранные.

        :param ayat_id: int
        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        """Добавить аят в избранные.

        :param chat_id: int
        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        """Удалить аят из избранных.

        :param chat_id: int
        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatRepository(AyatRepositoryInterface):
    """Интерфейс репозитория для работы с административными сообщениями."""

    def __init__(self, connection):
        self.connection = connection

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :returns: Ayat
        """
        query = """
            SELECT
                a.id,
                s.number as sura_num,
                s.link as sura_link,
                a.ayat as ayat_num,
                a.arab_text,
                a.content,
                a.trans as transliteration,
                cf.tg_file_id as audio_telegram_id,
                cf.link_to_file as link_to_audio_file
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE a.id = $1
        """
        row = await self.connection.fetchrow(query, ayat_id)
        return Ayat(**dict(row))

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Получить избранные аяты.

        :param chat_id: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.id,
                s.number as sura_num,
                s.link as sura_link,
                a.ayat as ayat_num,
                a.arab_text,
                a.content,
                a.trans as transliteration,
                cf.tg_file_id as audio_telegram_id,
                cf.link_to_file as link_to_audio_file
            FROM bot_init_subscriber_favourite_ayats fa
            INNER JOIN content_ayat a ON fa.ayat_id = a.id
            INNER JOIN bot_init_subscriber sub ON fa.subscriber_id = sub.id
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE sub.tg_chat_id = $1
        """
        rows = await self.connection.fetch(query, chat_id)
        return [
            Ayat(**dict(row))
            for row in rows
        ]

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.id,
                s.number as sura_num,
                s.link as sura_link,
                a.ayat as ayat_num,
                a.arab_text,
                a.content,
                a.trans as transliteration,
                cf.tg_file_id as audio_telegram_id,
                cf.link_to_file as link_to_audio_file
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE s.number = $1
        """
        records = await self.connection.fetch(query, sura_num)
        return [
            Ayat(**dict(record))
            for record in records
        ]

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Получить аят по номеру суры.

        :param ayat_id: int
        :param chat_id: int
        :returns: bool
        """
        query = """
            SELECT
                count(*)
            FROM bot_init_subscriber_favourite_ayats sub_ayat
            INNER JOIN bot_init_subscriber sub on sub.id = sub_ayat.subscriber_id
            where ayat_id = $1 and sub.tg_chat_id = $2
        """
        row = await self.connection.fetchrow(query, ayat_id, chat_id)
        return bool(row['count'])

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        """Добавить аят в избранные.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            INSERT INTO bot_init_subscriber_favourite_ayats
            (subscriber_id, ayat_id)
            VALUES
            (
                (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $1),
                $2
            )
        """
        await self.connection.execute(query, chat_id, ayat_id)

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        """Удалить аят из избранных.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            DELETE FROM bot_init_subscriber_favourite_ayats
            WHERE subscriber_id = (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $1) AND ayat_id = $2
        """
        await self.connection.execute(query, chat_id, ayat_id)
