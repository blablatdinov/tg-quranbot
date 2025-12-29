# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from srv.podcasts.parsed_podcast_reaction import ParsedPodcastReaction


@pytest.mark.parametrize(('callback_data', 'prayer_id', 'status'), [
    ('like(123)', 123, 'like'),
    ('dislike(7854)', 7854, 'dislike'),
])
def test(callback_data, prayer_id, status):
    reaction = ParsedPodcastReaction(callback_data)

    assert reaction.podcast_id() == prayer_id
    assert reaction.status() == status
