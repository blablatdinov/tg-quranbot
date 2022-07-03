from repository.ayats.ayat import Ayat, AyatRepositoryInterface


class AyatRepositoryMock(AyatRepositoryInterface):

    async def first(self) -> Ayat:
        return Ayat(
            id=34,
            sura_num=1,
            ayat_num='1-7',
            arab_text='some arab text',
            content='content',
            transliteration='transliteration',
            sura_link='/some-link',
            audio_telegram_id='some_id',
            link_to_audio_file='some-link',
        )


async def test():
    ayat = await AyatRepositoryMock().first()

    assert (
        str(ayat)
        == '<a href="https://umma.ru/some-link">1:1-7)</a>\nsome arab text\n\ncontent\n\n<i>transliteration</i>'
    )
