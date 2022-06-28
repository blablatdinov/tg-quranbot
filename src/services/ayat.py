from dataclasses import dataclass

from exceptions import AyatNotFoundError, SuraNotFoundError, exception_to_answer_formatter
from repository.ayats import Ayat, AyatRepositoryInterface
from services.answer import Answer, AnswerInterface


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

        :param ayat: Ayat
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру.

        :param search_input: str
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
        """Отформатировать аят для сообщения.

        :param ayat: Ayat
        :returns: str
        """
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

    @exception_to_answer_formatter
    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру.

        :param search_input: str
        :returns: AnswerInterface
        """
        sura_num, ayat_num = search_input.split(':')
        ayats = await self.ayat_repository.get_ayats_by_sura_num(sura_num)
        self._validate_sura_ayat_numbers(sura_num, ayat_num)
        for ayat in ayats:
            if '-' in ayat.ayat_num:
                answer = self._service_range_case(ayat, ayat_num)
            elif ',' in ayat.ayat_num:
                answer = self._service_comma_case(ayat, ayat_num)
            elif ayat.ayat_num == ayat_num:
                answer = Answer(message=self.format_ayat(ayat))

            if answer:
                return answer

        return Answer(message='Аят не найден')

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> AnswerInterface:
        left, right = map(int, ayat.ayat_num.split('-'))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return Answer(message=self.format_ayat(ayat))

    def _service_comma_case(self, ayat: Ayat, ayat_num: str):
        left, right = map(int, ayat.ayat_num.split(','))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return Answer(message=self.format_ayat(ayat))

    def _validate_sura_ayat_numbers(self, sura_num: int, ayat_num):
        max_sura_num = 114
        if not 0 < int(sura_num) < max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        if int(ayat_num) <= 0:
            raise AyatNotFoundError
