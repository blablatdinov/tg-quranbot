# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import pytest

from app_types.listable import AsyncListable
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.favorite_neighbor_ayats import FavoriteNeighborAyats
from srv.ayats.fk_ayat import FkAyat
from srv.ayats.fk_identifier import FkIdentifier
from srv.files.fk_file import FkFile


@final
@attrs.define(frozen=True)
class FkFavoriteAyats(AsyncListable[Ayat]):

    @override
    async def to_list(self) -> list[Ayat]:
        return [
            FkAyat(FkIdentifier(1, 1, '1-7'), '', FkFile.empty_ctor()),
            FkAyat(FkIdentifier(2, 1, '1-7'), '', FkFile.empty_ctor()),
            FkAyat(FkIdentifier(3, 1, '1-7'), '', FkFile.empty_ctor()),
        ]


@pytest.mark.parametrize(('ayat_id', 'expected'), [
    (1, 'стр. 1/3'),
    (2, 'стр. 2/3'),
    (3, 'стр. 3/3'),
])
async def test_page(ayat_id, expected):
    got = await FavoriteNeighborAyats(
        ayat_id, FkFavoriteAyats(),
    ).page()

    assert got == expected


async def test_left_neighbor_for_first_ayat():
    with pytest.raises(AyatNotFoundError):
        await FavoriteNeighborAyats(
            1, FkFavoriteAyats(),
        ).left_neighbor()


async def test_right_neighbor_for_last_ayat():
    with pytest.raises(AyatNotFoundError):
        await FavoriteNeighborAyats(
            3, FkFavoriteAyats(),
        ).right_neighbor()


async def test_neighbors_for_middle_ayat():
    left = await FavoriteNeighborAyats(
        2, FkFavoriteAyats(),
    ).left_neighbor()
    right = await FavoriteNeighborAyats(
        2, FkFavoriteAyats(),
    ).right_neighbor()

    assert await left.identifier().ayat_id() == 1
    assert await right.identifier().ayat_id() == 3
