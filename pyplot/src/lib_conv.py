# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as scp
import lib_background

def pattern(size):

    x = np.arange(size)
    y = np.arange(size)
    y = y[:, np.newaxis]

    x0 = np.floor(len(x) / 2)
    y0 = np.floor(len(y) / 2)

    print(x0, y0)

    pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / 2.25 ** 2)  # c'est tout bon pour x0 et y0

    return(pattern)

def extend(x,l):

    """
    Extend image with l lines and l columns on each side.

    """

    for i in range(l):
        x = np.insert(x, 0, 0, axis=1)

    top_bloc = np.array(l*[len(x[0])*[0]])
    x = np.concatenate((x, top_bloc), axis=0)
    x = np.concatenate((top_bloc, x), axis=0)

    side_bloc = np.array(len(x)*[l*[0]])
    x = np.concatenate((x, side_bloc), axis=1)

    return(x)

def scan(pixels, l, pattern):
    """
    Scan the original image and apply the pattern.
    """
    shape = np.shape(pixels)
    output = np.zeros((shape[0]-2*l, shape[1]-2*l), np.float)
    # Looping over
    for i in range(l, len(pixels)-l):
        for j in range(l, len(pixels[0])-l):
            # Create sub image 9x9 centered on pixel[i][j]
            image = pixels[i-l:i+l+1, j-l:j+l+1]
            output[i-l, j-l] = np.sum(image * pattern)

    return(output)

def neighbours(x, i,j):
    """
    Give access to all neighbours' values of a given pixel
    """
    next=[]
    for p in range(-1,2):
        for q in range(-1,2):
            next.append(x[i+p][j+q])
    next.remove(x[i][j])
    return(next)


def is_peak(x, i, j, threshold):

    okpeak = False

    if np.sum(x[i][j] > neighbours(x,i,j)) == 8 and x[i][j] > threshold:
        okpeak = True


    return(okpeak)

def peaks(pixels, l, threshold):
    peaks = []
    # Looping over
    for i in range(l, len(pixels) - l):
        for j in range(l, len(pixels[0]) - l):
            if is_peak(pixels, i, j, threshold):
                peaks.append([i-l,j-l])

    return(peaks)

def complete_peaks_search(pixels):

    # Build Gaussian pattern
    pat = pattern(9)
    sum_pat = np.sum(pat)
    pat = pat / sum_pat

    # Extend the image
    extended = extend(pixels, 4)

    # Convoluted
    conv = scan(extended, 4, pat)

    # Extend the convolution image
    conv_ext = extend(conv, 1)

    # Identify the Peaks
    thres = lib_background.threshold(pixels)
    print(thres)
    peaks_search = peaks(conv_ext, 1, thres)

    return(peaks_search)






