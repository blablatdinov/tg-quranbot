# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Literal, Protocol


class PodcastReactions(Protocol):
    """Реакция на подкаст."""

    def podcast_id(self) -> int:
        """Идентификатор подкаста."""

    def status(self) -> Literal['like', 'dislike']:
        """Реакция."""
