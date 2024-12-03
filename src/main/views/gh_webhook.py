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

"""Github webhook."""

import json

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from main.models import RepoStatusEnum
from main.service import get_or_create_repo, is_default_branch, update_config
from main.services.github_objs.gh_repo_installation import GhRepoInstallation


@csrf_exempt
def gh_webhook(request: HttpRequest) -> HttpResponse:  # noqa: PLR0911. TODO
    """Process webhooks from github."""
    with transaction.atomic():
        gh_event = request.headers.get('X-GitHub-Event')
        if not gh_event:
            return HttpResponse(status=422)
        request_json = json.loads(request.body)
        if gh_event == 'installation':
            installation_id = request_json['installation']['id']
            GhRepoInstallation(
                request_json['repositories'],
                installation_id,
            ).register()
            return HttpResponse('Repos installed')
        elif gh_event == 'installation_repositories':
            installation_id = request_json['installation']['id']
            GhRepoInstallation(
                request_json['repositories_added'],
                installation_id,
            ).register()
            return HttpResponse('Repos installed')
        pg_repo = get_or_create_repo(
            request_json['repository']['full_name'],
            int(request.headers['X-Github-Hook-Installation-Target-Id']),
        )
        if gh_event == 'ping':
            return HttpResponse('Webhooks installed')
        elif gh_event == 'push':
            if pg_repo.status != RepoStatusEnum.active:
                return HttpResponse('Skip as inactive')
            if not is_default_branch(request_json):
                return HttpResponse('Skip not default branch')
            update_config(request_json['repository']['full_name'])
            return HttpResponse('Config updated')
        return HttpResponse('Unprocessable event type')
