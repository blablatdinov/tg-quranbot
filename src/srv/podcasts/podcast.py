# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.files.tg_file import TgFile


class Podcast(TgFile, Protocol):
    """Интерфейс подкаста."""

    async def podcast_id(self) -> int:
        """Идентификатор аята."""
