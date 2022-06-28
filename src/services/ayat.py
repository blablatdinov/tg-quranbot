from dataclasses import dataclass

from repository.ayats import AyatRepositoryInterface, Ayat
from services.answer import AnswerInterface, Answer


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface

    async def get_formatted_first_ayat(self) -> str:
        """Получить отформатированный аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def format_ayat(self, ayat: Ayat) -> str:
        """Отформатировать аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface

    async def get_formatted_first_ayat(self) -> str:
        """Получить отформатированный аят.

        :returns: str
        """
        ayat = await self.ayat_repository.first()
        return self.format_ayat(ayat)

    def format_ayat(self, ayat: Ayat) -> str:
        link = 'https://umma.ru{sura_link}'.format(sura_link=ayat.sura_link)
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=link,
            sura=ayat.sura_num,
            ayat=ayat.ayat_num,
            arab_text=ayat.arab_text,
            content=ayat.content,
            transliteration=ayat.transliteration,
        )

    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру."""
        sura_num, ayat_num = search_input.split(':')
        ayats = await self.ayat_repository.get_ayats_by_sura_num(sura_num)
        for ayat in ayats:
            print('!!!!', ayat)
            print('!!!! ayat_num', ayat_num)
            print('!!!! db ayat_num', ayat.ayat_num)
            print('!!!! range', range(*list(map(int, ayat.ayat_num.split('-')))))
            if '-' in ayat.ayat_num:
                left, right = map(int, ayat.ayat_num.split('-'))
                ayats_range = range(left, right + 1)
                if int(ayat_num) in ayats_range:
                    return Answer(message=self.format_ayat(ayat))
            else:
                ayat = await self.ayat_repository.get_ayat_by_sura_ayat_num(sura_num, ayat_num)
                return Answer(message=self.format_ayat(ayat))
