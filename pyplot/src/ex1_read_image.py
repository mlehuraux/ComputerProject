#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np

def main():
    """ Exercise 1: Read Image """

    # analyse command line arguments
    file_name, interactive = args.get_args()

    # main tasks
    with fits.open(file_name) as fits_blocks:
        block = fits_blocks[0]

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
    """ Execute exercise 1 """
    sys.exit(main())
