# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def read_first_image(file_name):
    """ return header and pixels of a .fits file_name """
    pixels = None
    try : # open file_name
        with fits.open(file_name) as fits_blocks:
            block = fits_blocks[0]
            pixels = block.data
            header = block.header
    except IOError:
        print("Error while opening/reading file !")
        exit()
    except FileNotFoundError:
        print("Error with file name")
        exit()

    return header, pixels
