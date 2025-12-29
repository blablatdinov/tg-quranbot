# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypeAlias, final, override

import attrs

from services.intable_regex import IntableRegex
from srv.ayats.ayat_identifier import AyatId
from srv.ayats.favorite_ayat_status import FavoriteAyatStatus

# Строка имеющая формат addToFavor(<id аята>) или removeFromFavor(<id аята>)
_ChangeAyatStatusCommand: TypeAlias = str


@final
@attrs.define(frozen=True)
class AyatFavoriteStatus(FavoriteAyatStatus):
    """Пользовательский ввод статуса аята в избранном.

    >>> ayat_favor_status = AyatFavoriteStatus('addToFavor(14)')
    >>> ayat_favor_status.ayat_id()
    14
    >>> ayat_favor_status.change_to()
    True

    >>> ayat_favor_status = AyatFavoriteStatus('removeFromFavor(14)')
    >>> ayat_favor_status.ayat_id()
    14
    >>> ayat_favor_status.change_to()
    False
    """

    _source: _ChangeAyatStatusCommand

    @override
    def ayat_id(self) -> AyatId:
        """Идентификатор аята.

        :return: int
        """
        return int(IntableRegex(self._source))

    @override
    def change_to(self) -> bool:
        """Целевое значение.

        :return: bool
        """
        return 'addToFavor' in self._source
