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

"""Git repo from github."""

import datetime
from pathlib import Path
from typing import final, override

import attrs
import jwt
import requests
from django.conf import settings
from git import Repo

from main.models import GhRepo
from main.services.github_objs.cloned_repo import ClonedRepo
from main.services.github_objs.github_client import pygithub_client


@final
@attrs.define(frozen=True)
class GhClonedRepo(ClonedRepo):
    """Git repo from github."""

    _gh_repo: GhRepo

    @override
    def clone_to(self, path: Path) -> Path:
        """Cloning from github."""
        gh = pygithub_client(self._gh_repo.installation_id)
        repo = gh.get_repo(self._gh_repo.full_name)
        gh.close()
        now = int(datetime.datetime.now(tz=datetime.UTC).timestamp())
        signing_key = Path(settings.BASE_DIR / 'revive-code-bot.private-key.pem').read_bytes()
        payload = {'iat': now, 'exp': now + 600, 'iss': 874924}
        encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
        response = requests.post(
            'https://api.github.com/app/installations/{0}/access_tokens'.format(
                self._gh_repo.installation_id,
            ),
            headers={
                'Authorization': f'Bearer {encoded_jwt}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
            },
            timeout=5,
        )
        token = response.json()['token']
        Repo.clone_from(
            repo.clone_url.replace(
                'https://',
                'https://x-access-token:{0}@'.format(token),
            ),
            path,
        )
        return path
