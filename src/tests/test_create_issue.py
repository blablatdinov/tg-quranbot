# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from types import ModuleType

import pytest
from django.conf import settings

from main.models import GhRepo, TouchRecord
from main.service import process_repo
from main.services.github_objs.fk_cloned_repo import FkClonedRepo
from main.services.github_objs.fk_new_issue import FkNewIssue

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker: ModuleType) -> GhRepo:
    repo = baker.make(
        'main.GhRepo',
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )
    baker.make('main.RepoConfig', repo=repo, files_glob='**/*')
    return repo  # type: ignore [no-any-return]


@pytest.fixture
def _exist_touch_records(baker: ModuleType, gh_repo: GhRepo) -> None:
    files = [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    baker.make(
        'main.TouchRecord',
        gh_repo=gh_repo,
        path=(f for f in files),
        date=datetime.datetime.now(tz=datetime.UTC).date(),
    )


@pytest.mark.integration
def test(gh_repo: GhRepo) -> None:
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/iman-game-bot.zip'),
        new_issue,
    )
    today = datetime.datetime.now(tz=datetime.UTC).date()

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 5
    assert new_issue.issues[0] == {
        'title': 'Issue from revive-code-bot',
        'content': '\n'.join([
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
        ]),
    }


@pytest.mark.integration
@pytest.mark.usefixtures('_exist_touch_records')
def test_double_process(gh_repo: GhRepo) -> None:
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/iman-game-bot.zip'),
        new_issue,
    )
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
    assert new_issue.issues[0] == {
        'title': 'Issue from revive-code-bot',
        'content': '\n'.join([
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
        ]),
    }
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 10
