# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final

import attrs

from exceptions.base_exception import BaseAppError


@final
@attrs.define(frozen=True)
class UserAlreadyExistsError(BaseAppError):
    """Пользователь уже зарегистрирован."""

    admin_message = ''


@final
@attrs.define(frozen=True)
class StartMessageNotContainReferrerError(BaseAppError):
    """Стартовое сообщение не содержит информации о пригласившем."""

    admin_message = ''


@final
@attrs.define(frozen=True)
class UserAlreadyActiveError(BaseAppError):
    """Пользователь уже активен."""
