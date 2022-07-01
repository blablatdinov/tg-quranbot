from dataclasses import dataclass

from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.answer import AnswerInterface


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    async def get_by_id(self, ayat_id: int):
        """Получить аят по идентификатору.

        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    # def format_ayat(self, ayat: Ayat) -> str:
    #     """Отформатировать аят для сообщения.
    #
    #     :param ayat: Ayat
    #     :returns: str
    #     """
    #     link = 'https://umma.ru{sura_link}'.format(sura_link=ayat.sura_link)
    #     template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
    #     return template.format(
    #         link=link,
    #         sura=ayat.sura_num,
    #         ayat=ayat.ayat_num,
    #         arab_text=ayat.arab_text,
    #         content=ayat.content,
    #         transliteration=ayat.transliteration,
    #     )
