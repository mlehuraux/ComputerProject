# -*- coding: utf-8 -*-

"""
Definition of constants and helper functions shared by NPAC course scripts
"""

import sys

# Define some constants related to application exit status
EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_STANDARD_EXCEPTION = 1
EXIT_STATUS_PYTHON_TOO_OLD = 2
EXIT_STATUS_OPTION_ERROR = 3
EXIT_STATUS_CANCELED = 4
EXIT_STATUS_FAILURE = 5
EXIT_STATUS_PARTIAL_FAILURE = 6
EXIT_STATUS_GITLAB_EXCEPTION = 7
EXIT_STATUS_SONAR_EXCEPTION = 8

# Define some constants related to HTTP
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_ACCEPTED = 202
HTTP_STATUS_NO_CONTENT = 204
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_CONFLICT = 409
HTTP_STATUS_TOO_MANY_REQUESTS = 429
HTTP_REQUEST_RETRY_INTERVAL = 60     # in seconds
HTTP_REQUEST_MAX_RETRIES = 1


# Singleton decorator definition
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class GlobalParams:
    def __init__(self):
        self.gitlab_url = 'https://gitlab.lal.in2p3.fr/api/v4'
        self.sonar_url = 'https://sonar.lal.in2p3.fr/api'
        self.logger = None
        self.pygit2_installed = True
        self.sonar_token = None
        self.user_namespace = None
        self.user_token = None
        self.verbose = False



def debug(msg):
    global_params = GlobalParams()
    if global_params.logger:
        global_params.logger.debug(u'{}'.format(msg))
    elif global_params.verbose:
        print (msg)


def info(msg):
    global_params = GlobalParams()
    if global_params.logger:
        global_params.logger.info(u'{}'.format(msg))
    else:
        print (msg)


def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    global_params = GlobalParams()
    if global_params.verbose:
        debug_hook(exception_type, exception, traceback)
    else:
        print ("{}: {} (use --verbose for details)".format(exception_type.__name__, exception))


