# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeAlias

TgFileId: TypeAlias = str
FileLink: TypeAlias = str


class TgFile(Protocol):
    """Тип файла."""

    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм."""

    async def file_link(self) -> FileLink:
        """Ссылка на файл."""
