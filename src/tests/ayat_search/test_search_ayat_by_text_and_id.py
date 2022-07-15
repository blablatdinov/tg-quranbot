from services.ayats.search_by_text import AyatSearchByTextAndId


async def test(ayat_repository_mock):
    got = await AyatSearchByTextAndId(
        ayat_repository=ayat_repository_mock,
        query='content',
        ayat_id=1,
    ).search()

    assert got.title() == '1:1-7'
