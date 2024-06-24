from typing import final, override

import attrs
from pyeo import elegant

from srv.files.tg_file import FileLink, TgFile, TgFileId


@final
@attrs.define(frozen=True)
@elegant
class FkFile(TgFile):
    """Фейковый файл."""

    _file_id: str
    _link: str

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
