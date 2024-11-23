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

"""Test github webhook."""

from pathlib import Path

import pytest
from django.conf import settings
from django.test.client import Client

from main.models import GhRepo
from main.services.github_objs.github_client import pygithub_client

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def _remove_exist_webhook() -> None:
    gh = pygithub_client(52326552)
    gh_repo = gh.get_repo('blablatdinov/ramadan2020marathon_bot')
    hook = next(iter(
        hook
        for hook in gh_repo.get_hooks()
        if 'revive-code-bot.ilaletdinov.ru' in hook.config['url']
    ))
    hook.delete()


@pytest.mark.usefixtures('_remove_exist_webhook')
@pytest.mark.integration
def test_add_installation(client: Client) -> None:
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
        full_name='blablatdinov/ramadan2020marathon_bot',
        installation_id=52326552,
    ).count() == 1
