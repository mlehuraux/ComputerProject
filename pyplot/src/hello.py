#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Print a conventional message

:Author: Marion Lehuraux and François Claeys
:Date:   February 2018

First program hello.py: display "Hello, world!" on standard output.
"""

import sys

# By convention, a function name must contain only lowercase characters and _.
# txt=None defines a default value for string and makes it optional.
def printmsg(txt=None):
    """Print a message received as an argument or a default message
    if none is passed.

    :param txt: a string to print (optional)
    :return: status value (always success, 0)
    """

    if txt is None:
        # Define a default message
        txt = 'Hello, world!'
    print("{}".format(txt))
    return 0

# The following test is considered as a best practice: this way a module
# can be used both as a standalone application or as a module called by another
# module.
if __name__ == "__main__":

    # The main program is implemented mainly as a function: this avoids having
    # all the variables used in this context (e.g. text in print_msg) to
    # become global variables.
    status = printpsg()

    sys.exit(status)