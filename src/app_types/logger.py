# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class LogSink(Protocol):
    """Интерфейс объектов для логгирования."""

    def info(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, WPS110
        """Информационный уровень.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """

    def debug(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для отладки.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """

    def error(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для ошибок.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """

    def exception(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для исключений.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """
