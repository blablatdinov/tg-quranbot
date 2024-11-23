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

"""HTTP controllers."""

import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from main.models import GhRepo
from main.service import is_default_branch, process_repo, update_config
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.gh_repo_installation import GhRepoInstallation
from main.services.github_objs.github_client import pygithub_client


def healthcheck(request: HttpRequest) -> JsonResponse:
    """Endpoint for checking app."""
    return JsonResponse({
        'app': 'ok',
    })


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


@csrf_exempt
def process_repo_view(request: HttpRequest, repo_id: int) -> HttpResponse:
    """Webhook for process repo."""
    if request.headers['Authentication'] != 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN):
        raise PermissionDenied
    repo = get_object_or_404(GhRepo, id=repo_id)
    process_repo(
        repo.id,
        GhClonedRepo(repo),
        GhNewIssue(pygithub_client(repo.installation_id).get_repo(repo.full_name)),
    )
    return HttpResponse()


def connected_repos(request: HttpRequest) -> JsonResponse:
    """Endpoint for README badge.

    https://img.shields.io/badges/endpoint-badge
    """
    return JsonResponse({
        'schemaVersion': 1,
        'label': 'Connected repos',
        'message': str(GhRepo.objects.count()),
        'color': 'blue',
    })


def index(request: HttpRequest) -> HttpResponse:
    """Show index page."""
    return render(request, 'index.html')
