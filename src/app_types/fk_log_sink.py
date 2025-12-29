# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

from app_types.logger import LogSink


@final
class FkLogSink(LogSink):  # noqa: PEO200. Class for testing, has mutable state
    """Фейковый логгер."""

    stack: list[str]  # noqa: PEO300. Fake object

    def __init__(self) -> None:
        """Ctor."""
        self.stack = []  # noqa: PEO101. Fake object

    @override
    def info(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, WPS110
        """Информационный уровень.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """
        self.stack.append('INFO {0}'.format(args[0]))

    @override
    def debug(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для отладки.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """
        self.stack.append('DEBUG {0}'.format(args[0]))

    @override
    def error(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для ошибок.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """
        self.stack.append('ERROR {0}'.format(args[0]))

    @override
    def exception(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для исключений.

        :param args: tuple[object]
        :param kwargs: dict[object, object]
        """
        self.stack.append('ERROR {0}'.format(args[0]))
