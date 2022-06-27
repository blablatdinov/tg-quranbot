from dataclasses import dataclass

from repository.ayats import AyatRepositoryInterface


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface

    async def get_formatted_first_ayat(self) -> str:
        """Получить отформатированный аят.

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
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link='https://umma.ru' + ayat.sura_link,
            sura=ayat.sura_num,
            ayat=ayat.ayat_num,
            arab_text=ayat.arab_text,
            content=ayat.content,
            transliteration=ayat.transliteration,
        )
