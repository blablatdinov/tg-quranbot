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

"""Test github webhook."""

import re
from pathlib import Path

import pytest
from django.conf import settings

from main.models import GhRepo, RepoStatusEnum

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
def inactive_gh_repo(baker):
    repo = baker.make(
        'main.GhRepo',
        full_name='blablatdinov/gotemir',
        installation_id=1,
        status=RepoStatusEnum.inactive,
    )
    baker.make('main.RepoConfig', repo=repo)
    return repo


@pytest.fixture
def mock_scheduler(mock_http):
    mock_http.put(
        '{0}/api/jobs'.format(settings.SCHEDULER_HOST),
        status_code=200,
    )
    return mock_http


@pytest.fixture
def mock_github(mock_http):
    mock_http.register_uri(
        'POST',
        re.compile(r'https://api.github.com:443/app/installations/\d+/access_tokens'),
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_app_access_tokens_response.json').read_text(encoding='utf-8'),
    )
    mock_http.get(
        'https://api.github.com:443/repos/blablatdinov/gotemir',
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_repos_response.json').read_text(encoding='utf-8'),
    )
    mock_http.post(
        'https://api.github.com:443/repos/blablatdinov/gotemir/hooks',
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_hooks_response.json').read_text(encoding='utf-8'),
    )
    return mock_http


@pytest.fixture
def mock_github_permission_denied(mock_github):
    mock_github.register_uri(
        'GET',
        re.compile(r'https://api.github.com:443/repos/blablatdinov/gotemir/contents/.revive-bot.*'),
        status_code=403,
    )
    return mock_github


@pytest.fixture
def empty_revive_config(mock_github):
    mock_github.register_uri(
        'GET',
        re.compile(r'https://api.github.com:443/repos/blablatdinov/gotemir/contents/.revive-bot.*'),
        status_code=404,
        text='\n'.join([
            '{',
            '  "message": "Not Found",',
            '  "documentation_url": "https://docs.github.com/rest/repos/contents#get-repository-content",',
            '  "status": "404"',
            '}',
        ]),
    )


@pytest.fixture
def filled_revive_config(mock_github):
    mock_github.register_uri(
        'GET',
        re.compile(r'https://api.github.com:443/repos/blablatdinov/gotemir/contents/.revive-bot.*'),
        status_code=200,
        text='\n'.join([
            '{',
            '  "name": ".revive-bot.yml",',
            '  "path": ".revive-bot.yml",',
            '  "sha": "0d65cbc61abdd1ce508d90aa188d814f99eb1666",',
            '  "size": 30,',
            '  "url": "https://api.github.com/repos/blablatdinov/iman-game-bot/contents/.revive-bot.yml?ref=master",',
            '  "html_url": "https://github.com/blablatdinov/iman-game-bot/blob/master/.revive-bot.yml",',
            '  "git_url": "https://api.github.com/repos/blablatdinov/iman-game-bot/git/blobs/0d65cbc61abdd1ce508d90aa188d814f99eb1666",',
            '  "download_url": "https://raw.githubusercontent.com/blablatdinov/iman-game-bot/master/.revive-bot.yml",',
            '  "type": "file",',
            '  "content": "LS0tCmxpbWl0OiA1CmNyb246IDE2IDQgKiAqICoK\\n",',
            '  "encoding": "base64",',
            '  "_links": {',
            '    "self": "https://api.github.com/repos/blablatdinov/iman-game-bot/contents/.revive-bot.yml?ref=master",',
            '    "git": "https://api.github.com/repos/blablatdinov/iman-game-bot/git/blobs/0d65cbc61abdd1ce508d90aa188d814f99eb1666",',
            '    "html": "https://github.com/blablatdinov/iman-game-bot/blob/master/.revive-bot.yml"',
            '  }',
            '}',
        ]),
    )


@pytest.fixture
def mock_permission_denied(mock_http):
    mock_http.register_uri(
        'POST',
        re.compile(r'https://api.github.com:443/app/installations/\d+/access_tokens'),
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_app_access_tokens_response.json').read_text(encoding='utf-8'),
    )


@pytest.mark.usefixtures('gh_repo', 'empty_revive_config', 'mock_scheduler')
def test_empty_revive_config(anon):
    response = anon.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/push_event.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'push',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200


@pytest.mark.usefixtures('filled_revive_config', 'mock_scheduler')
def test_filled_revive_config(anon, gh_repo):
    response = anon.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/push_event.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'push',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    config = gh_repo.repoconfig_set.earliest('id')

    assert response.status_code == 200
    assert response.content == b'Config updated'
    assert config.cron_expression == '16 4 * * *'


@pytest.mark.usefixtures('empty_revive_config', 'mock_scheduler')
def test_add_installation(client) -> None:
    response = client.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/installation_added.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'installation_repositories',  # TODO: make test for other events
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200
    assert GhRepo.objects.filter(
        full_name='blablatdinov/gotemir',
        installation_id=52326552,
    ).count() == 1


@pytest.mark.usefixtures('empty_revive_config', 'mock_scheduler')
def test_add_single_installation(client) -> None:
    response = client.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/single_installation_added.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'installation',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200
    assert GhRepo.objects.filter(
        full_name='blablatdinov/gotemir',
        installation_id=52326552,
    ).count() == 1


@pytest.mark.usefixtures('mock_github_permission_denied')
def test_push_permission_denied(client, gh_repo) -> None:
    response = client.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/push_event.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'push',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    gh_repo.refresh_from_db()

    assert response.status_code == 200
    assert gh_repo.status == RepoStatusEnum.inactive


def test_skip_inactive_repo(anon, inactive_gh_repo):
    response = anon.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/push_event.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'push',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200
    assert response.content == b'Skip as inactive'


@pytest.mark.skip
def test_repo_not_found(anon):
    response = anon.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/push_event.json').read_text(encoding='utf-8'),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'push',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200
    assert response.content == b'Skip as inactive'
