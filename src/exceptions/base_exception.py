# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

class BaseAppError(Exception):  # noqa: FIN100
    """Базовое исключение бота."""


class InternalBotError(BaseAppError):  # noqa: FIN100
    """Внутренняя ошибка бота."""

    user_message = ''
