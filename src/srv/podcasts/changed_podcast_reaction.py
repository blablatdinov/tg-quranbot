# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Final, Protocol

PODCAST_ID_LITERAL: Final = 'podcast_id'
USER_ID_LITERAL: Final = 'user_id'


class ChangedPodcastReaction(Protocol):
    """Реакция на подкаст."""

    async def apply(self) -> None:
        """Применить."""
