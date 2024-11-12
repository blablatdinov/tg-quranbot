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
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from main.models import GhRepo
from main.service import GhClonedRepo, GhNewIssue, process_repo, pygithub_client, register_repo


def healthcheck(request):
    """Endpoint for checking app."""
    return JsonResponse({
        'app': 'ok',
    })


@csrf_exempt
def gh_webhook(request: HttpRequest):
    """Process webhooks from github."""
    # TODO wrap in transaction
    # TODO handle private repos
    if request.headers['X-GitHub-Event'] == 'installation_repositories':
        request_json = json.loads(request.body)
        installation_id = request_json['installation']['id']
        gh = pygithub_client(installation_id)
        register_repo(
            request_json['repositories_added'],
            installation_id,
            gh,
        )
        gh.close()
    elif request.headers['X-GitHub-Event'] == 'ping':
        request_json = json.loads(request.body)
        pg_repo = GhRepo.objects.get(full_name=request_json['repository']['full_name'])
        pg_repo.has_webhook = True
        pg_repo.save()
    return HttpResponse()


@csrf_exempt
def process_repo_view(request, repo_id: int):
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


def connected_repos(request):
    """Endpoint for README badge.

    https://img.shields.io/badges/endpoint-badge
    """
    return JsonResponse({
        'schemaVersion': 1,
        'label': 'Connected repos',
        'message': str(GhRepo.objects.count()),
        'color': 'blue',
    })
