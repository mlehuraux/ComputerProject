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
    # Allowed names for file_name
    names = ["common", "specific", "global", "dss.16.54.38.6-76.08.22.5"]

    try: # check if file_name exists as given by user
        file_name, interactive = args.get_args()
    except FileNotFoundError: # user can correct if previously wrong
        print('Files does not exist, file_name should be in : {}'.format(names))
        file_name = input('Enter file_name : \n')
        file_name = '../data/' + file_name + '.fits'
        interactive = input('Interactive mode [True/False] \n') # adjustment needed to define interactive without calling get_args()
        if interactive == 'True':
            interactive = True
        else :
            interactive = False

    header, pixels = lib_fits.read_first_image(file_name)

    #show figure
    if interactive:
        fig, main_axes = plt.subplots()
        imgplot = main_axes.imshow(pixels)
        plt.show()

    # example of console output - please replace it with your solutions!
    # ...
    #print('RESULT: file = {}'.format(file_name))
    #print('RESULT: interactive = {}'.format(interactive))

    signature_fmt_1 = header.get("CRPIX1")
    signature_fmt_2 = header.get("CRPIX2")
    print('RESULT: CRPIX1 = {:.0f}'.format(signature_fmt_1))
    print('RESULT: CRPIX2 = {:.0f}'.format(signature_fmt_2))

    return 0


if __name__ == '__main__':
    """ Execute exercise 1 """
    sys.exit(main())
