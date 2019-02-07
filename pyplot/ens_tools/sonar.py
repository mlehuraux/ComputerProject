# -*- coding: utf-8 -*-

"""
Definition of classes and functions shared by scripts used to manage NPAC accounts (SonarQube part)
"""

from datetime import date
from ens_tools.core import *

# FIXME: would be better to allow proper verification of the host certificate...
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SonarActionException(Exception):
    def __init__(self, action, msg):
        self.msg = "{}: {}".format(action, msg)
        self.status = EXIT_STATUS_SONAR_EXCEPTION

    def __str__(self):
        return repr(self.msg)


def create_sonar_token(user, force):
    global_params = GlobalParams()

    token = None
    today = date.today()
    token_name = 'NPAC {}-{}-{}'.format(today.year, today.month, today.day)

    debug("Creating access token '{}' for SonarQube user {}".format(token_name, user))
    debug('Authenticating as SonarQube admin (token={})'.format(global_params.sonar_token))

    url = '{}/user_tokens/search'.format(global_params.sonar_url)
    params = {'login':user}
    r = sonar_request(requests.get, url, auth=HTTPBasicAuth(global_params.sonar_token, ''), params=params)
    if r.status_code == HTTP_STATUS_OK:
        token_found = False
        for token_entry in r.json()['userTokens']:
            if token_entry['name'] == token_name:
                token_found = True
    else:
        raise SonarActionException("create_sonar_token",
                                   "Failed to retrieve access token list for Sonar user {} (status code={}, reason={})".format(user,
                                                                                                                               r.status_code,
                                                                                                                               r.reason))

    if token_found and not force:
        info("Sonar access token '{}' already exists for user {}. Use --regenerate to get it recreated.".format(token_name, user))
    else:
        if token_found:
            debug("Revoking existing access token '{}' for SonarQube user {}".format(token_name, user))
            url = '{}/user_tokens/revoke'.format(global_params.sonar_url)
            params = {'login': user, 'name': token_name}
            r = sonar_request(requests.post, url, auth=HTTPBasicAuth(global_params.sonar_token, ''), params=params)
            if r.status_code != HTTP_STATUS_NO_CONTENT:
                raise SonarActionException("create_sonar_token",
                                           "Failed to revoke access token for Sonar user {} (status code={}, reason={})".format(user,
                                                                                                                                r.status_code,
                                                                                                                                r.reason))

        url = '{}/user_tokens/generate'.format(global_params.sonar_url)
        params = {'login':user, 'name':token_name}
        r = sonar_request(requests.post, url, auth=HTTPBasicAuth(global_params.sonar_token, ''), params=params)
        if r.status_code == HTTP_STATUS_OK:
            token = r.json()['token']
            debug("Generated access token: {}".format(token))
        else:
            raise SonarActionException("create_sonar_token",
                                       "Failed to create an access token for Sonar user {} (status code={}, reason={})".format(user,
                                                                                                                               r.status_code,
                                                                                                                               r.reason))

    return token


def add_sonar_user(user, password):
    global_params = GlobalParams()

    debug('Creating SonarQube user {}'.format(user))
    debug('Authenticating as SonarQube admin (token={})'.format(global_params.sonar_token))

    url = '{}/users/search'.format(global_params.sonar_url)
    params = {'q':user}
    r = sonar_request(requests.post, url, auth=HTTPBasicAuth(global_params.sonar_token, ''), params=params)

    if r.status_code == HTTP_STATUS_OK and len(r.json()['users']) > 0:
        debug('Sonar user {} already exists: not recreated'.format(user))
    else:
        url = '{}/users/create'.format(global_params.sonar_url)
        params = {'login':user, 'name':user, 'password':password}
        r = sonar_request(requests.post, url, auth=HTTPBasicAuth(global_params.sonar_token, ''), params=params)

        if r.status_code != HTTP_STATUS_OK:
            raise SonarActionException("add_sonar_user",
                                        "Failed to create Sonar user {} (status code={}, reason={})".format(user,
                                                                                                            r.status_code,
                                                                                                            r.reason))


def sonar_request(request_method, *args, **kwords):
    """
    Function to encapsulate execution of a method from requests mode.

    :param request_method: method from requests module to execute
    :param args: mandatory arguments for the method
    :param kwords: positional arguments for the method
    :return: object returned by the method
    """

    r = request_method(*args, verify=False, **kwords)

    return r

