# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def create_histo(pixels, nbins):
    """Create histogram with nbins bins out of pixels 2D np.array"""
    global histo
    global bin_values
    global bin_boundaries

    histo = pixels.ravel()
    #print(histo)

    bin_values, bin_boundaries = np.histogram(histo, nbins)
    print("Histogram has been created !")

    fig, main_axes = plt.subplots()
    plt.hist(histo, nbins)
    plt.xlabel("Amplitude", fontsize=16)
    plt.ylabel("Frequency", fontsize=16)
    plt.title("Flux distribution", fontsize=20)
    plt.show()
    return 0

def modelling_function(x, p1, p2, p3):
    """
    Compute a gaussian function with parameters :
    p1 : maximum value
    p2 : mean value
    p3 : standard deviation sigma
    """
    y = p1 * np.exp(-(x - p2)**2 / (2 * p3**2))
    return y

def apply_model(input_array, p1, p2, p3):
    output_array = []
    for i in range(-10, 10):
        output_array.append(modelling_function(input_array[i], p1, p2, p3))
    return(np.array(output_array))
