#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args
import numpy as np
import matplotlib.pyplot as plt
import lib_fits
import lib_background

def main():
    """ Exercise 2: Background """

    # main tasks

    lib_fits.init()
    print(lib_fits.file_name)
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    lib_background.create_histo(pixels, 200)

    signature_fmt_1 = 'RESULT: histogram = {:d}'.format(lib_background.bin_values.sum())
    print(signature_fmt_1)




    # graphic output
    if lib_fits.interactive:
        # ...
        pass

    # end
    return 0


if __name__ == '__main__':
    """ Execute exercise 2 """
    sys.exit(main())
