# -*- coding: utf-8 -*-

"""
Definition of classes and functions shared by scripts used to manage NPAC accounts
"""

import sys
import time
import urllib.parse
from ens_tools.core import *


# FIXME: would be better to allow proper verification of the host certificate...
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class GitLabActionException(Exception):
    def __init__(self, action, msg):
        self.msg = "{}: {}".format(action, msg)
        self.status = EXIT_STATUS_GITLAB_EXCEPTION

    def __str__(self):
        return repr(self.msg)


class GitLabInvalidPassword(Exception):
    def __init__(self, action, msg):
        self.msg = "{}: {}".format(action, msg)
        self.status = EXIT_STATUS_GITLAB_EXCEPTION

    def __str__(self):
        return repr(self.msg)


class GitLabProjectNotFound(Exception):
    def __init__(self, user, project):
        self.msg = "Project '{}' not foud for user '{}'".format(project, user)
        self.status = EXIT_STATUS_GITLAB_EXCEPTION

    def __str__(self):
        return repr(self.msg)


def build_auth_header(user=None):
    """
    Build the http header to act as a user

    :param user: user to act as (if None, Sudo header is not added)
    :return: dict to use as the http header
    """

    global_params = GlobalParams()

    if user:
        return {'PRIVATE-TOKEN': global_params.user_token, 'Sudo': user}
    else:
        return {'PRIVATE-TOKEN': global_params.user_token}


def get_user_namespace(user=None):
    global_params = GlobalParams()

    if user:
        user_txt = user
    else:
        user_txt = "current user"
    debug("Retrieving {} namespace".format(user_txt))

    headers = build_auth_header(user)
    url = '{}/user'.format(global_params.gitlab_url)
    r = http_request(requests.get, url, headers=headers)
    debug('Status of namespace retrieval for current user: {} ({})'.format(r.status_code, r.reason))

    if r.status_code == HTTP_STATUS_UNAUTHORIZED:
        raise GitLabActionException('get_user_namespace',
                                    'Authorization failure with token {}'.format(global_params.user_token))
    elif r.status_code != HTTP_STATUS_OK:
        raise GitLabActionException('get_user_namespace',
                                    'Failed to retrieve namespace for user with token {}'.format(global_params.user_token))

    namespace = r.json()['username']
    debug('Current user GitLab namespace = {}'.format(namespace))
    return namespace


def get_project_id(project, user=None):
    global_params = GlobalParams()

    if user:
        user_txt = user
    else:
        user_txt = "current user"
    debug("Retrieving ID of GitLab project/repository {} (user={})".format(project, user_txt))

    headers = build_auth_header(user)
    project_namespace = get_user_namespace(user)
    project_name = urllib.parse.quote('{}/{}'.format(project_namespace, project), safe='')
    url = '{}/projects/{}'.format(global_params.gitlab_url, project_name)
    r = http_request(requests.get, url, headers=headers)
    debug('Project {} existence check status: {} ({})'.format(project, r.status_code, r.reason))
    if r.status_code == HTTP_STATUS_OK:
        project_id = r.json()['id']
        debug('Project {} exists for user {}: ID={}'.format(project, user, project_id))
    elif r.status_code == HTTP_STATUS_NOT_FOUND:
        raise GitLabProjectNotFound(user, project)
    else:
        raise GitLabActionException("get_project_id",
                                    "Failed to retrieve ID of project {} (status code={}, reason={})".format(project,
                                                                                                             r.status_code,
                                                                                                             r.reason))

    return project_id


def http_request(request_method, *args, **kwords):
    """
    Function to encapsulate execution of a method from requests mode and retry it in case
    the status code is 409 (TOO MANY CONNECTIONS). GitLab tends to throttle connections and temporarily
    to refuse new connections in case many of them happened in a short time (which is typically the case when
    creating a few tens of accounts). This functions pauses a little bit before retrying.

    :param request_method: method from requests module to execute
    :param args: mandatory arguments for the method
    :param kwords: positional arguments for the method
    :return: object returned by the method
    """

    attempt_num = 0
    request_status = HTTP_STATUS_TOO_MANY_REQUESTS
    while (attempt_num <= HTTP_REQUEST_MAX_RETRIES) and (request_status == HTTP_STATUS_TOO_MANY_REQUESTS):
        if attempt_num > 0:
            print ('WARNING: GitLab temporarily rejected the request: retrying in {}s'.format(HTTP_REQUEST_RETRY_INTERVAL))
            time.sleep(HTTP_REQUEST_RETRY_INTERVAL)
        r = request_method(*args, verify=False, **kwords)
        request_status = r.status_code
        attempt_num += 1

    if r.status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
        raise GitLabActionException('http_request',
                                    "GitLab rejected request with reason 'TOO MANY REQUEST': retry later")

    return r
