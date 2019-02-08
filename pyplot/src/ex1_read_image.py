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

    # Check that file_name is correct. If not, write it again and specify interactive
    try:
        file_name, interactive = args.get_args()
    except FileNotFoundError:
        print('Files does not exist, file_name should be in : {}'.format(names))
        file_name = input('Enter file_name : \n')
        file_name = '../data/' + file_name + '.fits'
        interactive = input('Interactive mode [True/False] \n')
        if interactive == 'True':
            interactive = True
        else :
            interactive = False

    # main tasks

    # Opennig the file, and check again it's name
    try :
        with fits.open(file_name) as fits_blocks:
            block = fits_blocks[0]
            pixels = block.data
    except FileNotFoundError:
        print("Error with file name")
        exit()

    #show figure
    if interactive:
        fig, main_axes = plt.subplots()
        imgplot = main_axes.imshow(pixels)
        plt.show()

    # example of console output - please replace it with your solutions!
    # ...
    print('RESULT: file = {}'.format(file_name))
    print('RESULT: interactive = {}'.format(interactive))

    # graphic output
    #if interactive:
        # ...
    #    pass

    # end
    return 0


if __name__ == '__main__':
    """ Execute exercise 1 """
    #sys.exit(main())
    header, pixels = lib_fits.read_first_image('common')
    signature_fmt_1 = header.get("CRPIX1")
    signature_fmt_2 = header.get("CRPIX2")
    print('RESULT: CRPIX1 = {:.0f}'.format(signature_fmt_1))
    print('RESULT: CRPIX2 = {:.0f}'.format(signature_fmt_2))
