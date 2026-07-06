# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final

import attrs

from exceptions.base_exception import BaseAppError


@final
@attrs.define(frozen=True)
class MessageTextNotFoundError(BaseAppError):
    """Текст сообщения не найден."""


@final
@attrs.define(frozen=True)
class CoordinatesNotFoundError(BaseAppError):
    """Координаты не найдены."""


@final
@attrs.define(frozen=True)
class CallbackQueryNotFoundError(BaseAppError):
    """Информация с кнопки не найдена."""


@final
@attrs.define(frozen=True)
class MessageIdNotFoundError(BaseAppError):
    """Идентификатор сообщения не найден."""


@final
@attrs.define(frozen=True)
class InlineQueryNotFoundError(BaseAppError):
    """Ошибка при отсутствии данных для поиска города."""


@final
@attrs.define(frozen=True)
class InlineQueryIdNotFoundError(BaseAppError):
    """Ошибка при отсутствии данных для поиска города."""
