from databases import Database
from pydantic import BaseModel, parse_obj_as


class ContentSpam(BaseModel):
    """Модель для рассылки утреннего контента."""

    chat_id: int
    content: str  # noqa: WPS110
    link: str


class AyatMorningContentRepositoryInterface(object):
    """Интерфейс для работы с хранилищем данных для рассылок."""

    async def get_morning_content(self) -> list[ContentSpam]:
        """Получить контент для рассылки.
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatMorningContentRepository(AyatMorningContentRepositoryInterface):
    """Класс для работы с хранилищем данных для рассылок."""

    def __init__(self, connection: Database):
        self._connection = connection

    async def get_morning_content(self) -> list[ContentSpam]:
        """Получить контент для рассылки.
        :returns: list[ContentSpam]
        """
        query = """
            SELECT
                s.chat_id,
                STRING_AGG(
                    '<b>' || sura.sura_id::CHARACTER VARYING || ': ' || a.ayat_number || ')</b> ' || a .content || '\n',
                    ''
                    ORDER BY a.ayat_id
                ) AS content,
                STRING_AGG(sura.link, '|' ORDER BY a.ayat_id) AS link
            FROM users AS s
            LEFT JOIN ayats AS a ON a.day=s.day
            LEFT JOIN suras AS sura ON a.sura_id=sura.sura_id
            WHERE s.is_active = 't'
            GROUP BY s.chat_id
        """
        rows = await self._connection.fetch_all(query)
        return parse_obj_as(list[ContentSpam], [row._mapping for row in rows])  # noqa: WPS437
