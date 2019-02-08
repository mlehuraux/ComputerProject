# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def create_histo(pixels, nbins):
    global histo
    global bin_values
    global bin_boundaries

    histo = pixels.ravel()
    #print(histo)

    bin_values, bin_boundaries = np.histogram(histo, nbins)
    print("Histogram has been created !")

    fig, main_axes = plt.subplots()
    plt.hist(histo, nbins)
    plt.show()
