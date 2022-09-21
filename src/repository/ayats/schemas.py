from pydantic import BaseModel


class AyatShort(BaseModel):
    """Короткая модель аята."""

    id: int
    sura_num: int
    ayat_num: str

    def title(self) -> str:
        """Заголовок.

        :returns: str
        """
        return '{0}:{1}'.format(self.sura_num, self.ayat_num)


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

    def get_short(self) -> AyatShort:
        """Трансформировать в короткую версию.

        :returns: AyatShort
        """
        return AyatShort(id=self.id, ayat_num=self.ayat_num, sura_num=self.sura_num)
