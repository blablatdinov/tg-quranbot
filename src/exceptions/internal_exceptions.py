# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

# flake8: noqa: WPS202

from typing import final, override

import attrs

from exceptions.base_exception import BaseAppError


@final
class NotFoundReferrerIdError(BaseAppError):
    """Исключение возбуждается в случае если невозможно зарегистрировать пользователя с рефералом."""

    user_message = 'Невозможно зарегистрировать пользователя с рефералом'


@final
class UserNotFoundError(BaseAppError):
    """Исключение возбуждается в случае если пользователь не найден."""

    user_message = 'Пользователь не найден'


@final
class UserHasNotGeneratedPrayersError(BaseAppError):
    """У пользователя нет сгенерированных времен намаза на текущий день."""

    admin_message = ''


@final
class NotProcessableUpdateError(BaseAppError):
    """Исключение, вызываемое если бот не знает как обработать запрос."""

    admin_message = ''


@final
@attrs.define(frozen=True)
class TelegramIntegrationsError(BaseAppError):
    """Исключение, возбуждаемое при некорректном ответе от API телеграмма."""

    _message: str
    admin_message = 'Ошибка интеграции telegram'

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return self._message


@final
@attrs.define(frozen=True)
class UnreacheableError(BaseAppError):
    """Ошибка непредвиденного состояния."""


@final
@attrs.define(frozen=True)
class PrayerAtUserAlreadyExistsError(BaseAppError):
    """У пользователя уже сгенерированы времена намазов."""


@final
@attrs.define(frozen=True)
class PrayerAlreadyExistsError(BaseAppError):
    """Времена намазов на эту дату и город уже существуют."""


@final
@attrs.define(frozen=True)
class PrayerAtUserNotCreatedError(BaseAppError):
    """Времена намазов не созданы."""


@final
@attrs.define(frozen=True)
class PrayerNotCreatedError(BaseAppError):
    """Времена намазов не созданы."""


@final
@attrs.define(frozen=True)
class CityNotFoundError(BaseAppError):
    """Город не найден."""
