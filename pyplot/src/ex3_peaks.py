#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args
import lib_fits
import lib_background
import numpy as np
import matplotlib.pyplot as plt


def main():
    """ Exercise 3: Peaks """

    lib_fits.init()
    print(lib_fits.file_name)
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    x = np.arange(9)
    y = np.arange(9)
    y = y[:,np.newaxis]

    print(x)

    x0 = np.floor(len(x)/2)
    y0 = np.floor(len(y)/2)

    print(x0, y0)

    pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / 2.25 ** 2) # c'est tout bon pour x0 et y0


    plt.imshow(pattern)
    plt.show()

    sum_pat = np.sum(pattern)
    sum_pat_norm = sum_pat/sum_pat
    max_pat = np.max(pattern)
    max_pat_norm = max_pat / sum_pat


    signature_fmt_1 = 'RESULT: pattern_sum={:.5f}'.format(sum_pat_norm)
    signature_fmt_2 = 'RESULT: pattern_max={:.5f}'.format(max_pat_norm)
    print(signature_fmt_1)
    print(signature_fmt_2)






    # main tasks
    # ...

    # example of console output - please replace it with your solutions!
    # ...
    #print('RESULT: file = {}'.format(file_name))
    #print('RESULT: interactive = {}'.format(interactive))

    # graphic output
    if lib_fits.interactive:
        # ...
        pass

    # end
    return 0


if __name__ == '__main__':
    """ Execute exercise 3 """
    sys.exit(main())
