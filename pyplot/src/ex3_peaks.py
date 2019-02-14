#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from npac import args
import lib_fits
import lib_background
import numpy as np
import matplotlib.pyplot as plt
import lib_conv


def main():
    """ Exercise 3: Peaks """


    lib_fits.init()
    print(lib_fits.file_name)
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    # Build Gaussian pattern
    pattern = lib_conv.pattern(9)
    plt.imshow(pattern)
    #plt.show()

    sum_pat = np.sum(pattern)
    pattern = pattern/sum_pat
    sum_pat_norm = np.sum(pattern)
    max_pat_norm = np.max(pattern)


    signature_fmt_1 = 'RESULT: pattern_sum={:.5f}'.format(sum_pat_norm)
    signature_fmt_2 = 'RESULT: pattern_max={:.5f}'.format(max_pat_norm)
    print(signature_fmt_1)
    print(signature_fmt_2)

    # Extend the image
    extended = lib_conv.extend(pixels, 4)
    plt.imshow(extended)
    plt.show()

    height = len(extended)
    width = len(extended[0])
    sum = np.sum(extended)

    signature_fmt_3 = 'RESULT: extended_image_width={:d}'.format(width)
    signature_fmt_4 = 'RESULT: extended_image_height={:d}'.format(height)
    signature_fmt_5 = 'RESULT: extended_image_sum={:.0f}'.format(sum)

    print(signature_fmt_3)
    print(signature_fmt_4)
    print(signature_fmt_5)


    # Convoluted

    conv = lib_conv.scan(extended, 4, pattern)

    plt.imshow(conv)
    plt.show()

    conv_height = len(conv)
    conv_width = len(conv[0])
    conv_sum = np.sum(conv)

    signature_fmt_6 = 'RESULT: convoluted_image_width={:d}'.format(conv_width)
    signature_fmt_7 = 'RESULT: convoluted_image_height={:d}'.format(conv_height)
    signature_fmt_8 = 'RESULT: convoluted_image_sum={:.0f}'.format(conv_sum)

    print(signature_fmt_6)
    print(signature_fmt_7)
    print(signature_fmt_8)

    # Extend the convolution image

    conv_ext = lib_conv.extend(conv, 1)

    conv_ext_height = len(conv_ext)
    conv_ext_width = len(conv_ext[0])
    conv_ext_sum = np.sum(conv_ext)

    signature_fmt_9 = 'RESULT: extended_convoluted_image_width={:d}'.format(conv_ext_width)
    signature_fmt_10 = 'RESULT: extended_convoluted_image_height={:d}'.format(conv_ext_height)
    signature_fmt_11 = 'RESULT: extended_convoluted_image_sum={:.0f}'.format(conv_ext_sum)

    print(signature_fmt_9)
    print(signature_fmt_10)
    print(signature_fmt_11)

    # Identify the Peaks


    threshold = lib_background.threshold(pixels)
    print(threshold)
    peaks = lib_conv.peaks(conv_ext, 1, threshold)

    signature_fmt_12 = 'RESULT: peaks_number={:d}'.format(len(peaks))

    print(signature_fmt_12)

    # end
    return 0


if __name__ == '__main__':
    """ Execute exercise 3 """
    sys.exit(main())
