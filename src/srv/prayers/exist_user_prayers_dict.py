# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypedDict, final


@final
class ExistUserPrayersDict(TypedDict):
    """ExistUserPrayersDict."""

    prayer_at_user_id: int
    is_read: bool
