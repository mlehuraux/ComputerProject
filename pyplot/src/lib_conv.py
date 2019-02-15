# -*- coding: utf-8 -*-
import numpy as np
import lib_background

def pattern(size):
    """
    Give the 2D array convolution pattern for a given size.
    """

    x = np.arange(size)
    y = np.arange(size)
    y = y[:, np.newaxis]

    x0 = np.floor(len(x) / 2)
    y0 = np.floor(len(y) / 2)

    print(x0, y0)

    pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / 2.25 ** 2)  # c'est tout bon pour x0 et y0

    return(pattern)

def extend(pixels,margin):
    """
    Extend image with margin lines and margin columns on each side.
    """

    for i in range(margin):
        pixels = np.insert(pixels, 0, 0, axis=1)

    top_bloc = np.array(margin*[len(pixels[0])*[0]])
    pixels = np.concatenate((pixels, top_bloc), axis=0)
    pixels = np.concatenate((top_bloc, pixels), axis=0)

    side_bloc = np.array(len(pixels)*[margin*[0]])
    pixels = np.concatenate((pixels, side_bloc), axis=1)

    return(pixels)

def scan(pixels, margin, pattern):
    """
    Scan the original image and apply the pattern.
    """
    shape = np.shape(pixels)
    output = np.zeros((shape[0]-2*margin, shape[1]-2*margin), np.float)
    # Looping over
    for i in range(margin, len(pixels)-margin):
        for j in range(margin, len(pixels[0])-margin):
            # Create sub image 9x9 centered on pixel[i][j]
            image = pixels[i-margin:i+margin+1, j-margin:j+margin+1]
            output[i-margin, j-margin] = np.sum(image * pattern)

    return(output)

def neighbours(pixels,i,j):
    """
    Give access to all neighbours' values of a given pixel.
    """
    next=[]
    for p in range(-1,2):
        for q in range(-1,2):
            next.append(pixels[i+p][j+q])
    next.remove(pixels[i][j])
    return(next)


def is_peak(x, i, j, threshold):
    """
    For a pixel, To be a peak or not to be a peak, that is the question.
    This function gives the answer.
    """
    okpeak = False

    if np.sum(x[i][j] > neighbours(x,i,j)) == 8 and x[i][j] > threshold:
        okpeak = True


    return(okpeak)

def peaks(pixels, margin, threshold):
    """
    Returns list of all the peaks.
    """
    peaks = []

    # Looping over all pixel of the image.
    for i in range(margin, len(pixels) - margin):
        for j in range(margin, len(pixels[0]) - margin):
            if is_peak(pixels, i, j, threshold):
                peaks.append([i-margin,j-margin])

    return(peaks)

def complete_peaks_search(pixels):
    """
    From pixels; retunrs directly the list of peaks, going through convoluted imgage.
    Result of ex3.
    """

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






