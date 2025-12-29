# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Literal, final, override

import attrs

from app_types.stringable import SupportsStr
from services.intable_regex import IntableRegex
from srv.podcasts.podcast_reactions import PodcastReactions


@final
@attrs.define(frozen=True)
class ParsedPodcastReaction(PodcastReactions):
    """Реакция на подкаст.

    >>> prayer_reaction = ParsedPodcastReaction('like(17)')
    >>> prayer_reaction.podcast_id()
    17
    >>> prayer_reaction.status()
    'like'
    """

    _callback_query: SupportsStr

    @override
    def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return int(IntableRegex(str(self._callback_query)))

    @override
    def status(self) -> Literal['like', 'dislike']:
        """Реакция.

        :return: Literal['like', 'dislike']
        """
        if 'dislike' in str(self._callback_query):
            return 'dislike'
        return 'like'
