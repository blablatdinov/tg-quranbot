# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.files.tg_file import FileLink, TgFile, TgFileId


@final
@attrs.define(frozen=True)
class FkFile(TgFile):
    """Фейковый файл."""

    _file_id: str
    _link: str

    @classmethod
    def empty_ctor(cls) -> TgFile:
        """Конструктор для создания объекта с пустыми значениями."""
        return cls('', '')

    @override
    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм.

        :return: TgFileId
        """
        return self._file_id

    @override
    async def file_link(self) -> FileLink:
        """Идентификатор файла в телеграм.

        :return: FileLink
        """
        return self._link
