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

from main.models import GhRepo
from main.service import is_default_branch, update_config
from main.services.github_objs.gh_repo_installation import GhRepoInstallation
from main.services.github_objs.github_client import pygithub_client


@csrf_exempt
def gh_webhook(request: HttpRequest) -> HttpResponse:
    """Process webhooks from github."""
    with transaction.atomic():
        gh_event = request.headers.get('X-GitHub-Event')
        if not gh_event:
            return HttpResponse(status=422)
        request_json = json.loads(request.body)
        if gh_event in {'installation', 'installation_repositories'}:
            installation_id = request_json['installation']['id']
            gh = pygithub_client(installation_id)
            GhRepoInstallation(
                request_json['repositories_added'],
                installation_id,
                gh,
            )
            gh.close()
        elif gh_event == 'ping':
            pg_repo = GhRepo.objects.get(full_name=request_json['repository']['full_name'])
            pg_repo.has_webhook = True
            pg_repo.save()
        elif gh_event == 'push':
            if not is_default_branch(request_json):
                return HttpResponse()
            update_config(request_json['repository']['full_name'])
        return HttpResponse()
