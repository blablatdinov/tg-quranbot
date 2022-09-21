from services.ayats.favorite_ayats import FavoriteAyatStatus


def test():
    favor_status = FavoriteAyatStatus('addToFavor(12)')

    assert favor_status.ayat_id() == 12
    assert favor_status.change_to() is True
