#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args

def main():
    """ Exercise 2: Background """

    # analyse command line arguments
    file_name, interactive = args.get_args()

    # main tasks
    # ...

    # example of console output - please replace it with your solutions!
    # ...
    print('RESULT: file = {}'.format(file_name))
    print('RESULT: interactive = {}'.format(interactive))

    # graphic output
    if interactive:
        # ...
        pass

    # end
    return 0


if __name__ == '__main__':
    """ Execute exercise 2 """
    sys.exit(main())
