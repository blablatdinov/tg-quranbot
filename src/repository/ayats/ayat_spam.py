from asyncpg import Connection
from pydantic import BaseModel, parse_obj_as


class ContentSpam(BaseModel):
    """Модель для рассылки утреннего контента."""

    chat_id: int
    content: str  # noqa: WPS110
    link: str


class AyatSpamRepositoryInterface(object):
    """Интерфейс для работы с хранилищем данных для рассылок."""

    async def get_content_for_spam(self) -> list[ContentSpam]:
        """Получить контент для рассылки.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatSpamRepository(AyatSpamRepositoryInterface):
    """Класс для работы с хранилищем данных для рассылок."""

    def __init__(self, connection: Connection):
        self._connection = connection

    async def get_content_for_spam(self) -> list[ContentSpam]:
        """Получить контент для рассылки.

        :returns: list[ContentSpam]
        """
        query = """
            SELECT
                s.tg_chat_id as chat_id,
                STRING_AGG(
                    '<b>' || sura.number::CHARACTER VARYING || ': ' || a.ayat || ')</b> ' || a .content || '\n',
                    ''
                    ORDER BY a.id
                ) AS content,
                STRING_AGG(sura.link, '|' ORDER BY a.id) AS link
            FROM bot_init_subscriber AS s
            LEFT JOIN content_morningcontent AS mc ON s.day=mc.day
            LEFT JOIN content_ayat AS a ON a.one_day_content_id=mc.id
            LEFT JOIN content_sura AS sura ON a.sura_id=sura.id
            WHERE s.is_active = 't'
            GROUP BY s.tg_chat_id
        """
        rows = await self._connection.fetch(query)
        return parse_obj_as(list[ContentSpam], rows)
