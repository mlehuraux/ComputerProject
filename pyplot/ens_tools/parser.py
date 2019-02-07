# -*- coding: utf-8 -*-

"""
Definition of exceptions and other classes rekated to option parsing in NPAC course scripts
"""

import argparse
from ens_tools.core import *

class OptionParsingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class OptionParsingExit(Exception):
    def __init__(self, status, msg):
        self.msg = "{} (return code={})".format(msg, status)
        self.status = EXIT_STATUS_OPTION_ERROR

    def __str__(self):
        return repr('{} (status={})'.format(self.msg, self.status))


class MissingReqOptionException(Exception):
    def __init__(self, option):
        self.msg = "Missing required option '--{}'".format(option)
        self.status = EXIT_STATUS_OPTION_ERROR

    def __str__(self):
        return repr(self.msg)


class ModifiedOptionParser(argparse.ArgumentParser):
    @classmethod
    def error(cls, msg):
        raise OptionParsingError(msg)

    @classmethod
    def exit(cls, status=0, msg=None):
        raise OptionParsingExit(status, msg)

    def invalid_option_value(self, msg):
        """
        Method to report an invalid option or option value and to exit the application with an exit code = 2.

        :param msg: message to be printed before the help itself
        """

        print (msg)
        self.print_help()
        sys.exit(EXIT_STATUS_OPTION_ERROR)


