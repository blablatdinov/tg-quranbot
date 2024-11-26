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

"""Test process repo."""

import re
from pathlib import Path

import pytest
from django.conf import settings

from main.models import RepoStatusEnum

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker):
    repo = baker.make(
        'main.GhRepo',
        full_name='blablatdinov/gotemir',
        installation_id=1,
        status=RepoStatusEnum.active,
    )
    baker.make('main.RepoConfig', repo=repo)
    return repo


@pytest.fixture
def mock_github(mock_http):
    mock_http.register_uri(
        'POST',
        re.compile(r'https://api.github.com:443/app/installations/\d+/access_tokens'),
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_app_access_tokens_response.json').read_text(encoding='utf-8'),
    )
    mock_http.get(
        'https://api.github.com:443/repos/blablatdinov/gotemir',
        status_code=403,
    )
    return mock_http


@pytest.mark.integration
def test(anon, repo) -> None:
    response = anon.post(
        '/process-repo/{0}'.format(repo.id),
        headers={
            'Authentication': 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN),
        },
    )

    assert response.status_code == 200


@pytest.mark.usefixtures('mock_github')
def test_permission_denied(anon, gh_repo):
    response = anon.post(
        '/process-repo/{0}'.format(gh_repo.id),
        headers={
            'Authentication': 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN),
        },
    )

    gh_repo.refresh_from_db()

    assert response.status_code == 200
    assert gh_repo.status == RepoStatusEnum.inactive
