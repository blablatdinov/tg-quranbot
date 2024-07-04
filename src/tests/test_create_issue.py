# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Test create issue."""

import datetime
from operator import attrgetter

import pytest

from main.models import TouchRecord
from main.service import process_repo, pygithub_client

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def gh_repo(mixer):
    yield mixer.blend(
        'main.GhRepo',
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )
    repo = pygithub_client(52326552).get_repo('blablatdinov/iman-game-bot')
    for issue in repo.get_issues():
        if issue.title == 'Issue from revive-code-bot':
            issue.edit(state='closed')


@pytest.fixture()
def _exist_touch_records(mixer, gh_repo):
    files = [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    mixer.cycle(5).blend(
        'main.TouchRecord',
        gh_repo=gh_repo,
        path=(f for f in files),
        date=datetime.datetime.now(tz=datetime.UTC).date(),
    )


def test(gh_repo, time_machine):
    process_repo(gh_repo.id)
    today = datetime.datetime.now(tz=datetime.UTC).date()

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 5
    assert next(iter(sorted(
        pygithub_client(gh_repo.installation_id).search_issues('Issue from revive-code-bot'),
        key=attrgetter('created_at'),
        reverse=True,
    ))).body == '\n'.join([
        '- [ ] `manage.py`',
        '- [ ] `game/views.py`',
        '- [ ] `game/migrations/__init__.py`',
        '- [ ] `game/apps.py`',
        '- [ ] `game/__init__.py`',
        '',
        '',
        'Expected actions:',
        '1. Create new issues with reference to this issue',
        '2. Clean files must be marked in checklist',
        '3. Close issue',
    ])


@pytest.mark.usefixtures('_exist_touch_records')
def test_double_process(gh_repo):
    process_repo(gh_repo.id)
    today = datetime.datetime.now(tz=datetime.UTC).date()

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
        'config/wsgi.py',
        'config/asgi.py',
        'bot_init/urls.py',
        'bot_init/migrations/__init__.py',
        'bot_init/migrations/0001_initial.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 10
    assert next(iter(sorted(
        pygithub_client(gh_repo.installation_id).search_issues('Issue from revive-code-bot'),
        key=attrgetter('created_at'),
        reverse=True,
    ))).body == '\n'.join([
        '- [ ] `config/wsgi.py`',
        '- [ ] `config/asgi.py`',
        '- [ ] `bot_init/urls.py`',
        '- [ ] `bot_init/migrations/__init__.py`',
        '- [ ] `bot_init/migrations/0001_initial.py`',
        '',
        '',
        'Expected actions:',
        '1. Create new issues with reference to this issue',
        '2. Clean files must be marked in checklist',
        '3. Close issue',
    ])
