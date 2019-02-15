#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import lib_fits

def main():
    """ Exercise 1: Read Image """
    #taking file name

    lib_fits.init()
    print(lib_fits.file_name)
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)


    # show figure
    if lib_fits.interactive:
        fig, main_axes = plt.subplots()
        main_axes.imshow(pixels)
        plt.show()

    #signature

    signature_fmt_1 = 'RESULT: CRPIX1 = {:.0f}'.format(header.get("CRPIX1"))
    signature_fmt_2 = 'RESULT: CRPIX2 = {:.0f}'.format(header.get("CRPIX2"))
    print(signature_fmt_1)
    print(signature_fmt_2)

    return 0


if __name__ == '__main__':
    """ Execute exercise 1 """
    sys.exit(main())