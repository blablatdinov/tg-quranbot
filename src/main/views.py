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
from contextlib import suppress

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.exceptions import PermissionDenied
from github.GithubException import UnknownObjectException
from github.Repository import Repository

from main.models import GhRepo, AnalyzeJobsSchedule
from main.service import pygithub_client, generate_default_config, read_config, process_repo, GhClonedRepo, GhNewIssue


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
        for repo in request_json['repositories_added']:
            repo_db_record = GhRepo.objects.create(
                full_name=repo['full_name'],
                installation_id=installation_id,
                has_webhook=False,
            )
            gh_repo = gh.get_repo(repo['full_name'])
            gh_repo.create_hook(
                'web', {
                    'url': 'https://www.rehttp.net/p/https%3A%2F%2Frevive-code-bot.ilaletdinov.ru%2Fhook%2Fgithub',
                    'content_type': 'json',
                },
                ['issues', 'issue_comment', 'push'],
            )
            config = _read_config_from_repo(gh_repo)
            AnalyzeJobsSchedule.objects.create(repo=repo_db_record, cron_expression=config['cron'])
        gh.close()
    elif request.headers['X-GitHub-Event'] == 'ping':
        request_json = json.loads(request.body)
        pg_repo = GhRepo.objects.get(full_name=request_json['repository']['full_name'])
        pg_repo.has_webhook = True
        pg_repo.save()
    return HttpResponse()


def _read_config_from_repo(gh_repo: Repository):
    # TODO write tests
    # TODO invalid cron in .revive-bot.yaml case
    variants = ('.revive-bot.yaml', '.revive-bot.yml')
    for variant in variants:
        with suppress(UnknownObjectException):
            return read_config(
                gh_repo
                .get_contents(variant)
                .decoded_content
                .decode('utf-8'),
            )
    return generate_default_config()


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
