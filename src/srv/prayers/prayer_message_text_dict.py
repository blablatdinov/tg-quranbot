# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypedDict, final


@final
class PrayerMessageTextDict(TypedDict):
    """Словарь с данными для отправки пользователю."""

    city_name: str
    date: str
    fajr_prayer_time: str
    sunrise_prayer_time: str
    dhuhr_prayer_time: str
    asr_prayer_time: str
    magrib_prayer_time: str
    ishaa_prayer_time: str
