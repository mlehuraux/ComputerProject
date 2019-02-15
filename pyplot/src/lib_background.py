# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as scp

def create_histo(pixels, nbins):
    """
    Create histogram with nbins bins out of pixels 2D array.
    """
    global histo
    global bin_values
    global bin_boundaries

    histo = pixels.ravel()
    #print(histo)

    bin_values, bin_boundaries = np.histogram(histo, nbins)
    print("Histogram has been created !")

    return 0

def modelling_function(x, p1, p2, p3):
    """
    Compute a gaussian function with parameters :
    p1 : maximum value,
    p2 : mean value,
    p3 : standard deviation sigma.
    """
    y = p1 * np.exp(-(x - p2)**2 / (2 * p3**2))
    return y

def apply_model(input_array, p1, p2, p3):
    """
    Compute expected value of modeling function on input_array.
    """

    output_array = []
    for i in range(len(input_array)):
        output_array.append(modelling_function(input_array[i], p1, p2, p3))
    return(np.array(output_array))

def normalize(bin_values, bin_boundaries):
    """
    Normalize the histogram.
    """
    mval = np.float(np.max(bin_values))
    mbound = np.float(np.max(bin_boundaries))
    normal_val = bin_values/mval
    normal_bound = bin_boundaries[:-1]/mbound
    return(normal_val, normal_bound)

def max_array(input):
    """
    Extract max value of input_array.
    """
    return(np.float(np.max(input)))

def fit_and_return(normal_bound, normal_val):
    """
    Fit the histogram and return the un-normalized fit parameters.
    """
    fit, covariant = scp.curve_fit(modelling_function, normal_bound, normal_val)

    maxvalue = fit[0] * max_array(bin_values)
    background = fit[1] * max_array(bin_boundaries)
    dispersion = fit[2] * max_array(bin_boundaries)

    return(maxvalue, background, dispersion)

def plotting(x1, y1, y2):
    """
    Plot the original histogram and its fit.
    """
    fig, main_axes = plt.subplots()
    plt.plot(x1, y1, 'b+:', label='data')
    plt.plot(x1, y2, 'r.:', label='fit')

    plt.xlabel("Amplitude", fontsize=16)
    plt.ylabel("Frequency", fontsize=16)
    plt.title("Flux distribution", fontsize=20)

    plt.legend()


    plt.show()

    return 0


def threshold(pixels):
    """
    From the pixels 2D array, fits the histogram.
    From fit parameters, give the threshold.
    """

    create_histo(pixels, 200)

    norm_val, norm_bound = normalize(bin_values, bin_boundaries)

    results = fit_and_return(norm_bound, norm_val)

    background = results[1]
    dispersion = results[2]

    threshold = background + 6.0 * dispersion

    return(threshold)






