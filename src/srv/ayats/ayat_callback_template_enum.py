# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import enum
from typing import final


@final
class AyatCallbackTemplateEnum(enum.StrEnum):
    """Шаблон для метаинформации кнопки."""

    get_ayat = 'getAyat({0})'
    get_favorite_ayat = 'getFAyat({0})'
    get_search_ayat = 'getSAyat({0})'
