# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final

import attrs

from exceptions.base_exception import BaseAppError


@final
@attrs.define(frozen=True)
class UserPrayersNotFoundError(BaseAppError):
    """У пользователя нет сгенерированных времен намазов."""

    admin_message = ''


@final
@attrs.define(frozen=True)
class PrayersNotFoundError(BaseAppError):
    """Не найдены времена намазов."""

    city_name: str
    date: datetime.date


@final
@attrs.define(frozen=True)
class PrayersAlreadyExistsError(BaseAppError):
    """Произошла попытка дублирования строк в таблице prayers."""
