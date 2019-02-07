#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to check a commit status on GitLab when GitLab CI is used on the repository. Typical usage:

check_commit_status --token your_token --repository repo_name --download-logs

with 'your_token' the access token retrieved from GitLab web interface (Profile Settings->Account) and 'repo_name'
the gitLab project name. Use --help for all the options.

This application can also be called a Python module. Typical calling sequence is:

from check_commit_status import commit_status_check,set_options
ccs_options = set_options(repository='student', branch='master', build_job='pyplot-checks', user='npacxx')
status_text = commit_status_check(ccs_options)

A configuration file can be used to define the GitLab access token and a few filtering expressions applied to build
log files. If the same configuration file is used, the result will be the same whether this application is invoked as
as a script or as a module.
"""

import os
import sys

PYTHON_MIN = (3, 5)
major, minor, _, _, _ = sys.version_info
if (major, minor) < PYTHON_MIN:
    python_min_str = '.'.join(str(x) for x in PYTHON_MIN)
    # Keep old formatter syntax to be sure it works with old version of Python
    print ("This script requires Python %s or later" % python_min_str)
    sys.exit(2)

import logging
import io
import re
from urllib.request import Request
import yaml

from ens_tools.gitlab import *
from ens_tools.parser import *

_author = "Michel Jouvin"
__version__ = "2.0.0"


# Some constants
BUILD_STATUS_FAILED = 'failed'
BUILD_STATUS_PENDING = 'pending'
BUILD_STATUS_RUNNING = 'running'
BUILD_STATUS_SUCCESS = 'success'
CONFIG_FILE_DEFAULT = 'ens_tools/check_commit_status.cfg'
CONFIG_MAIN_SECTION = 'DEFAULT'
COMMIT_VALID_PATTERN = re.compile(r'^([0-9a-fA-F]+|last)$')


def pygit2_unavailable():
    """
    Function to register that pygit2 is not available. Used to avoid
    declaring a global variable.

    :return: none
    """
    global_params = GlobalParams()
    global_params.pygit2_installed = True


# pygit2 is rarely installed by default... Can be installed with PIP.
# Register whether it is available or not...
try:
    import pygit2 as git
except ImportError:
    print ('pygit2 module not found: install it to be able to guess the repository/branch to use')
    pygit2_unavailable()


# 'builds' in recent GitLab is called 'jobs'
def get_commit_builds(project_id, branch=None, commit=None, job=None):
    global_params = GlobalParams()

    if not branch and not commit:
        debug("Retrieving default branch in repository {}".format(project_id))
        params = build_auth_header()
        url = '{}/projects/{}'.format(global_params.gitlab_url, project_id)
        r = http_request(requests.get, url, params=params)
        debug('Status of default branch retrieval: {} ({})'.format(r.status_code, r.reason))
        branch = r.json()['default_branch']

    if commit:
        commit_sha = commit
        branch_msg = 'commit {}'.format(commit)
    else:
        commit_sha = branch
        branch_msg = 'branch {}'.format(branch)

    debug("Retrieving last commit ({})".format(branch_msg))
    params = build_auth_header()
    url = '{}/projects/{}/repository/commits/{}'.format(global_params.gitlab_url, project_id, commit_sha)
    r = http_request(requests.get, url, headers=params)
    debug('Status of last commit retrieval in {}: {} ({})'.format(branch_msg, r.status_code, r.reason))

    if r.status_code == HTTP_STATUS_OK:
        last_commit_id = r.json()['id']
    elif r.status_code == HTTP_STATUS_NOT_FOUND:
        raise GitLabActionException('get_commit_builds',
                                    '{} not found'.format(branch_msg))
    else:
        raise GitLabActionException('get_commit_builds',
                                    'Failed to retrieve last commit from branch {} project ID {} (status code={}, reason={})'.format(branch,
                                                                                                                                     project_id,
                                                                                                                                     r.status_code,
                                                                                                                                     r.reason))

    params = build_auth_header()
    url = '{}/projects/{}/repository/commits/{}/statuses'.format(global_params.gitlab_url, project_id, last_commit_id)
    r = http_request(requests.get, url, headers=params)
    debug('Status of commit builds retrieval: {} ({})'.format(r.status_code, r.reason))

    if r.status_code == HTTP_STATUS_OK:
        build_entries = r.json()
        if len(build_entries) >= 0:
            debug("{} builds (pipelines) found for commit {}".format(len(build_entries), last_commit_id))
            #debug(json.dumps(build_entries, sort_keys=True, indent=4, separators=(',', ': ')))
            # If name of a build job has been specified, return only the entries matching this job and raise an
            # exception if no entry is matching the job name
            if job:
                debug("Selecting build entries matching build job '{}'".format(job))
                job_builds = []
                for entry in build_entries:
                    if entry['name'] == job:
                        job_builds.append(entry)
                if len(job_builds) > 0:
                    build_entries = job_builds
                else:
                    raise GitLabActionException('get_commit_status',
                                                'No build entry found matching job {} for commit {} in repository ID {}'.format(
                                                                                                job, last_commit_id, project_id))
        else:
            raise GitLabActionException('get_commit_status',
                                        'No build found for commit {} in repository ID {}'.format(last_commit_id,project_id))
    else:
        raise GitLabActionException('get_commit_status',
                                    'Failed to retrieve build for commits{} (status code={}, reason={})'.format(last_commit_id,
                                                                                                                r.status_code,
                                                                                                                r.reason))
    return build_entries


def get_repo_last_commit(project_id):
    """
    Retrieve last commit in the repository, whatever branch it is in

    :param project_id: the project ID
    :return: ID of the last commit in the repository
    """

    global_params = GlobalParams()

    debug("Retrieving last commit in repository for project ID {}".format(project_id))

    headers = build_auth_header()
    url = '{}/projects/{}/repository/branches'.format(global_params.gitlab_url, project_id)
    r = http_request(requests.get, url, headers=headers)

    if r.status_code == HTTP_STATUS_OK:
        branches = sorted(r.json(), key=lambda branch: branch["commit"]["created_at"], reverse=True)
        return branches[0]['commit']['id']
    else:
        raise GitLabActionException('get_repo_last_commit',
                                    'Failed to retrieve branch list (status={}, reason={})'.format(r.status_code, r.reason))


def print_commit_status(project_id, branch=None, commit=None, job=None):
    global_params = GlobalParams()

    if commit:
        if commit == 'last':
            commit = get_repo_last_commit(project_id)
        commit_msg = 'commit {}'.format(commit)
        branch_msg = ''
    else:
        commit_msg = 'last commit'
        if branch:
            branch_msg = ' (branch {})'.format(branch)
        else:
            branch_msg = ' (default branch)'

    if job:
        job_msg = ' (build job={})'.format(job)
    else:
        job_msg = ''

    debug("Computing and printing status of {}{} for project ID {}{}".format(commit_msg, branch_msg, project_id, job_msg))

    build_entries = get_commit_builds(project_id, branch=branch, commit=commit, job=job)

    # Compute global status of the build in case several jobs where executed and build the list of failed jobs
    global_status = BUILD_STATUS_SUCCESS
    failed_builds_ids = []
    entry_id = 0
    for entry in build_entries:
        if entry['status'] != BUILD_STATUS_SUCCESS:
            if entry['status'] == BUILD_STATUS_FAILED:
                # Keep track of the failed build ID (index in the build_entries list)
                failed_builds_ids.append(entry_id)
            if (global_status == BUILD_STATUS_SUCCESS) or (global_status == BUILD_STATUS_RUNNING):
                # If global_status is success or running, update it with the entry status
                global_status = entry['status']
            elif (global_status != BUILD_STATUS_FAILED) and (entry['status'] == BUILD_STATUS_FAILED):
                # If global_status is not failed and the entry status is failed, update it
                global_status = entry['status']
        entry_id += 1


    pipeline_prefix = ''
    if not job:
        global_params.logger.info(u'CI status of {}{}: {}'.format(commit_msg, branch_msg, global_status))
        # Ident status of pipeline entries
        pipeline_prefix = '    '

    for entry in build_entries:
        global_params.logger.info(u'{}Pipeline {}: {} (date={})'.format(pipeline_prefix,
                                                                       entry['name'],
                                                                       entry['status'],
                                                                       entry['created_at']))

    return build_entries, failed_builds_ids


def download_build_log(project_id, build, summary_only=False, patterns=None, failed_job=False):
    global_params = GlobalParams()

    debug("Downloading trace file for build {}".format(build['id']))
    if summary_only:
        debug('Download only summary lines (pattern={})'.format(patterns))
    else:
        if patterns:
            debug("Filtering out lines matching pattern '{}'".format(patterns))

    params = build_auth_header()
    url = '{}/projects/{}/jobs/{}/trace'.format(global_params.gitlab_url, project_id, build['id'])
    r = http_request(requests.get, url, headers=params)
    debug('Status of trace download: {} ({})'.format(r.status_code, r.reason))

    if r.status_code != HTTP_STATUS_OK:
        raise GitLabActionException('download_build_log',
                                    'Failed to download build {} log file (status={}, reason={})'.format(build['id'],
                                                                                                         r.status_code,
                                                                                                         r.reason))

    # First select content lines according to the criteria given
    log_lines = []
    for line in r.content.splitlines():
        # Convert the line to a UTF-8 string: required for Python3, useless but harmless for Python2
        line = line.decode('utf-8')
        selected_line = None
        # Only lines matching one of the patterns will be displayed
        if summary_only:
            for pattern in patterns:
                m = re.match(pattern, line)
                if m:
                    selected_line = line
                    break
        # All lines not matching any of the patterns are displayed.
        # If no patterns have been specified, all lines are displayed
        else:
            if patterns:
                display_line = True
                for pattern in patterns:
                    m = re.match(pattern, line)
                    if m:
                        display_line = False
                        break
                if display_line:
                    selected_line = line
            else:
                selected_line = line
        if selected_line:
            log_lines.append(selected_line)
        else:
            debug('DEBUG: line filtered out={}'.format(line))

    # Ignore empty files if summary_only and if the job has been successful
    if len(log_lines) > 0:
        title = u'Log file for pipeline {} (status={}, date={})'.format(build['name'], build['status'], build['created_at'])
        title_len = len(title)
        global_params.logger.info(u'')
        global_params.logger.info (title_len * u'-')
        global_params.logger.info (title)
        global_params.logger.info (title_len * u'-')
        for line in log_lines:
            global_params.logger.info (line)
        global_params.logger.info (title_len * u'-')


def git_current_branch():
    global_params = GlobalParams()
    default_branch_name = None
    default_repository = None

    debug('Checking if current directory is a Git repository and retrieving current branch')

    # Repository() method in pygit2 requires the actual directory containing the .git directory,
    # not one of its children like the git command. Walk up from the current directory to find it.
    dir_candidate = os.getcwd()
    previous_dir_candidate = ''
    while dir_candidate != previous_dir_candidate:
        git_repo = '{}/.git'.format(dir_candidate)
        if os.path.exists(git_repo):
            debug("Git repository found in {}".format(dir_candidate))
            break
        else:
            debug("git repository not found in {}. Looking in parent dir...".format(dir_candidate))
            previous_dir_candidate = dir_candidate
            dir_candidate = os.path.dirname(dir_candidate)

    try:
        repository = git.Repository(dir_candidate)
        default_branch_name = repository.head.shorthand
        if default_branch_name == 'HEAD':
            default_branch_name = None
            return  default_branch_name, default_repository
        else:
            debug('Default branch set to {}'.format(default_branch_name))
    except KeyError:
        debug('Current directory is not a Git repository: no default branch or repository defined')

    # Retrieve remote associated with current branch
    default_branch = repository.lookup_branch(default_branch_name)
    remote_branch = default_branch.upstream
    if not remote_branch:
        debug('Current branch ({}) is not tracking a remote branch: default repository cannot be defined'.format(default_branch_name))
        return  default_branch_name, default_repository
    remote_name = remote_branch.remote_name
    # Retrieve remote URL
    remotes = repository.remotes
    head_remote = filter(lambda r: r.name == remote_name, remotes)
    # Python2: filter() returns a list, Python3: filter() returns a filter object
    if not isinstance(head_remote, list):
        head_remote = list(head_remote)
    debug('Remote {} URL = {}'.format(remote_name, head_remote[0].url))
    m = re.match('(\w+://)*(\w+@)*(?P<host>.*):.*/(?P<repo>.*)', head_remote[0].url)
    if m:
        remote_host = m.group('host')
        remote_repository = m.group('repo')
        # Remove .git from repo name if present
        m2 = re.match('(?P<repo>.*)(?=\.git)', remote_repository)
        if m2:
            remote_repository = m2.group('repo')
        debug('Remote host = {}, remote repository = {}'.format(remote_host, remote_repository))
    else:
        raise GitLabActionException('get_current_branch',
                                    'Error parsing remote {} url ({})'.format(remote_name, head_remote[0].url))
    # Retrieve host name of GitLab server
    req = Request(url=global_params.gitlab_url)
    gitlab_host = req.host
    m = re.match('(?P<host>.*)(\:\d+)', gitlab_host)
    if m:
        gitlab_host = m.group('host')
    else:
        gitlab_host = req.host
    if remote_host == gitlab_host:
        default_repository = remote_repository
        debug('Default repository set to {}'.format(default_repository))
    else:
        debug("Remote {} host doesn't match the GitLab host ({}): default repository cannot be defined")

    return default_branch_name, default_repository


def load_config_file(config_file):
    global_params = GlobalParams()

    config_options = None
    try:
        with open(config_file) as f:
            config_options = yaml.load(f)
        debug('config_options (from config file): {}'.format(repr(config_options)))
    except IOError as e:
        if e.errno == 2:
            global_params.logger.error('Configuration file ({}) is missing.'.format(config_file))
        else:
            raise Exception('Error opening configuration file ({}): {} (errno={})'.format(config_file, e.strerror, e.errno))
    except (yaml.parser.ParserError,yaml.scanner.ScannerError) as e:
        raise Exception('Configuration file ({}) has an invalid format: ({})'.format(config_file, e))

    return config_options


def set_options(options=None,
                all_job_logs=None,
                branch=None,
                build_job=None,
                commit=None,
                config_file=None,
                download_logs=None,
                raw_logs=None,
                repository=None,
                summary_only=None,
                token=None,
                user=None,
                verbose=None):
    """
    Function to initialize/update options. Basically mimics what is done by argparser in main().
    Not ideal but allows to call this application as a module rather than a command.
    Be sure to maintain the consistency with what argparser does in main().

    :param options: a argparse.Namespace() object that will be updated if provided or created if None
    :param all_job_logs: --all-job-logs
    :param branch:   --branch
    :param build_job: --build-job
    :param commit: --commit
    :param config_file: --config-file
    :param download_logs: --downloadd-logs
    :param raw_logs: --raw-logs
    :param repository: --repository
    :param summary_only: --summary
    :param token: --token
    :param user: --user
    :param verbose: --verbose
    :return: the updated options
    """

    # For clarity, define default values here. Note that they cannot be defined as default values of arguments
    # as it would become impossible to distingish between a specified and unspecified argument and make impossible
    # to call this function multiple times without affecting all the options.
    all_job_logs_default = False
    branch_default = None
    build_job_default = None
    commit_default = None
    config_file_default = CONFIG_FILE_DEFAULT
    download_logs_default = False
    raw_logs_default = False
    repository_default = None
    summary_only_default = True
    token_default = None
    user_default = None
    verbose_default = False

    # Initialize options if None
    if not options:
        options = argparse.Namespace()

    # Apply specified or default values for all options
    if all_job_logs:
        options.all_job_logs = all_job_logs
    elif not 'all_job_logs' in options:
        options.all_job_logs = all_job_logs_default
    if branch:
        options.branch = branch
    elif not 'branch' in options:
        options.branch = branch_default
    if build_job:
        options.build_job = build_job
    elif not 'build_job' in options:
        options.build_job = build_job_default
    if commit:
        options.commit = commit
    elif not 'commit' in options:
        options.commit = commit_default
    if config_file:
        options.config_file = config_file
    elif not 'config_file' in options:
        options.config_file = config_file_default
    if download_logs:
        options.download_logs = download_logs
    elif not 'download_logs' in options:
        options.download_logs = download_logs_default
    if raw_logs:
        options.raw_logs = raw_logs
    elif not 'raw_logs' in options:
        options.raw_logs = raw_logs_default
    if repository:
        options.repository = repository
    elif not 'repository' in options:
        options.repository = repository_default
    if summary_only:
        options.summary_only = summary_only
    elif not 'summary_only' in options:
        options.summary_only = summary_only_default
    if token:
        options.token = token
    elif not 'token' in options:
        options.token = token_default
    if user:
        options.user = user
    elif not 'user' in options:
        options.user = user_default
    if verbose:
        options.verbose = verbose
    elif not 'verbose' in options:
        options.verbose = verbose_default

    # Check mutually exclusive options checked by the argparser
    if options.branch and options.commit:
        raise OptionParsingError("'branch' ({}) and 'commit' ({})  options are mutually exclusive".format(options.branch, options.commit))

    return options


def commit_status_check(options=None, logger=None):
    """
    Function doing the real work whether it is called as a script (through main() function) or directly as a module.
    If logger is not defined, assume it is called as a module and create one with a StreamHandler associated with a
    StringIO object that will be used at the return value.

    :param options: a argparse.Namespace() object that will be updated if provided or created if None
    :param logger: a logger instance
    :return: logger stream contents if no logger was passed (called as a module)
    """

    global_params = GlobalParams()
    script_output = None

    # Initialize logger if none was passed as argument and set default level to INFO
    if logger:
        global_params.logger =  logger
    else:
        global_params.logger = logging.getLogger(__name__)
        script_output = io.StringIO()
        ch = logging.StreamHandler(stream=script_output)
        global_params.logger.addHandler(ch)
    global_params.logger.setLevel(logging.INFO)

    # Initialize options if they were not defined, applying defaults.
    # Should not occur when executed as a command, only when used as a module.
    # After this point, the application will behave the same whether it was called as a
    # command or as a module.
    if not options:
        options = set_options(None)

    # Update logger level if --verbose option has been specified
    if options.verbose:
        global_params.logger.setLevel(logging.DEBUG)

    # If --user is specified --repository and --branch or --comit are required (non sense to guess
    # them from local user)
    if options.user and (not options.repository or not (options.branch or options.commit)):
        raise OptionParsingError('--user specified: --repository and --branch or --commit required')

    # Read options from optional config file
    # If config file is not absolute, prefix with directory where this script resides
    if not os.path.isabs(options.config_file):
        this_script_dir = os.path.dirname(__file__)
        if len(this_script_dir) == 0:
            this_script_dir = os.path.curdir
        # Do not use os.sep as it doesn't work in a bash shell on Windows
        options.config_file = '/'.join((this_script_dir, options.config_file))
    config_options = load_config_file(options.config_file)

    # Read user GitLab token from the command line option if present. Else retrieve it from the configuration file
    # and if it is not defined, raise an error. In the configuration file, use 'gitlab_tokens' option if a user
    # has been explicitly specified with --user else `gitlab_token`
    if options.token:
        global_params.user_token = options.token
    elif config_options and options.user and 'gitlab_tokens' in config_options:
        if options.user in config_options['gitlab_tokens']:
            global_params.user_token = config_options['gitlab_tokens'][options.user]
        else:
            raise Exception("GitLab access token for user {} not defined in the configuration file".format(options.user))
    elif config_options and not options.user and 'gitlab_token' in config_options:
        global_params.user_token = config_options['gitlab_token']
    else:
        raise Exception("GitLab access token defined neither on command line nor in the configuration file")

    if options.repository:
        repository = options.repository
    if options.branch:
        branch = options.branch
    if not options.repository or (not options.branch and not options.commit):
        try:
            import pygit2 as git
            default_branch, default_repository = git_current_branch()
            if not options.repository:
                repository = default_repository
            if not options.branch:
                branch = default_branch
        except ImportError:
            raise Exception("Module pygit2 not available: --branch or --commit required")

    # At this point repository MUST be defined (either explicitely or guessed from current directory if it is a Git repo)
    # and branch MUST be defined except if --commit has been specified.
    if not repository:
        raise Exception("Default repository could not be retrieved from current directory: --repository required")
    if options.commit:
        # Check that the commit ID is a valid value
        if not COMMIT_VALID_PATTERN.match(options.commit):
            raise Exception("'{}' is not a valid commit ID".format(options.commit))
        # branch must not be defined when commit is defined
        branch = None
    elif not branch:
        raise Exception("Default branch could not be retrieved from current directory: --branch required")

    # Check/retrieve options related to logs download if necessary
    log_patterns = None
    if options.raw_logs and not options.download_logs:
        raise OptionParsingError('--raw-logs specified without --download-logs')
    if options.download_logs and options.summary_only:
        # --download_logs/--raw_logs win
        options.summary_only = False
    if options.summary_only:
        if 'summary_patterns' in config_options:
            debug('Summary patterns = {}'.format(config_options['summary_patterns']))
            log_patterns = config_options['summary_patterns']
        else:
            raise OptionParsingError("--summary requested but no 'summary_patterns' defined in configuration file ({})".format(config_file))
    elif options.download_logs and not options.raw_logs and 'filter_patterns' in config_options:
        debug('Filter patterns = {}'.format(config_options['filter_patterns']))
        log_patterns = config_options['filter_patterns']

    try:
        global_params.user_namespace = get_user_namespace()
        project_id = get_project_id(repository)
        build_entries, failed_builds_ids = print_commit_status(project_id, branch=branch, commit=options.commit, job=options.build_job)
        if options.download_logs or options.summary_only:
            # If --download_log has been specified, download the log files for failed jobs only
            # if --all-job-logs has not been also specified. If only the summary lines are requested
            # return them for all jobs which produced some.
            if options.download_logs and not options.all_job_logs:
                selected_entries = failed_builds_ids
            else:
                selected_entries = range(len(build_entries))
            for entry_id in selected_entries:
                if entry_id in failed_builds_ids:
                    failed_job = True
                else:
                    failed_job = False
                download_build_log(project_id, build_entries[entry_id], summary_only=options.summary_only, patterns=log_patterns, failed_job=failed_job)
    except GitLabActionException as e:
        global_params.logger.error(e.msg)
        global_params.logger.error("Failed to check commit status for repository {}".format(repository))
    except:
        raise

    if script_output:
        output_txt = script_output.getvalue()
    else:
        output_txt = ''
    return output_txt


def main():
    """
    This function is used to parse arguments when the module is called as a script from command line.
    After argument parsing, it calls commit_status_check which does the real work.

    :return: scrpit exit status code
    """

    global_params = GlobalParams()

    # Initialize a logger sending output to stdout
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(ch)

    try:
        parser = ModifiedOptionParser()
        parser.add_argument("--build-job", dest="build_job", help="Name of build job to check")
        parser.add_argument("--config-file", dest="config_file", default=CONFIG_FILE_DEFAULT,
                            help="Configuration file for this utility")
        parser.add_argument("-r", "--repository", dest="repository", help="GitLab project to check")
        parser.add_argument("--verbose", action="store_true", dest="verbose", default=False,
                            help="Print debugging information")
        parser.add_argument("--version", action="version", version='%(prog)s {}'.format(__version__))
        user_opts = parser.add_mutually_exclusive_group()
        user_opts.add_argument("-t", "--token", help="GitLab user token (required if not in the config file)")
        user_opts.add_argument("-u", "--user", help="GitLab user to check instead of the current user")
        commit_opts = parser.add_mutually_exclusive_group()
        commit_opts.add_argument("-b", "--branch", help="Branch to check")
        commit_opts.add_argument("-c", "--commit", help="Commit to check or 'last' for the last commit in the repository")
        logs_opts = parser.add_argument_group('build logs', 'Options related to download of build logs')
        download_opts = logs_opts.add_mutually_exclusive_group()
        download_opts.add_argument("--download-logs", action="store_true", dest="download_logs", default=False,
                            help="Download log files of failed builds (lines filtered)")
        download_opts.add_argument("--no-summary", action="store_false", dest="summary_only",
                                  help="Do not download the summary lines of build logs")
        logs_opts.add_argument("--all-job-logs", action="store_true", dest="all_job_logs", default=False,
                               help="Download logs/summary for all jobs, not just failed ones")
        logs_opts.add_argument("--raw-logs", action="store_true", dest="raw_logs", help="Do not filter downloaded build logs")
        options = parser.parse_args()
    except OptionParsingError as e:
        parser.invalid_option_value('Parsing error: {}'.format(e.msg))
        return EXIT_STATUS_OPTION_ERROR
    except OptionParsingExit as e:
        logger.error('The option parser exited with message {}'.format(e.msg))
        return EXIT_STATUS_OPTION_ERROR

    # check_commit_status() does the real job and raise exceptions in case of errors
    commit_status_check(options=options, logger=logger)

    return EXIT_STATUS_SUCCESS


if __name__ == '__main__':
    sys.excepthook = exception_handler
    sys.exit(main())
