# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypeAlias, final, override

import attrs

from app_types.stringable import SupportsStr
from services.intable_regex import IntableRegex

_AyatNum: TypeAlias = str


@final
@attrs.define(frozen=True)
class AyatLink(SupportsStr):
    """Ссылка на аят.

    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '1-5'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-1'
    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '6, 7'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-6'
    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '15-18'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-15'
    """

    _sura_link: str
    _sura_num: int
    _ayat_num: _AyatNum

    @override
    def __str__(self) -> str:
        """Формирование ссылки с якорем на аят.

        Пример: https://umma.ru/sura-56-al-vaky-a-sobytie/#56-18

        :return: str
        """
        return 'https://umma.ru{0}#{1}-{2}'.format(
            self._sura_link,
            self._sura_num,
            int(IntableRegex(self._ayat_num)),
        )
