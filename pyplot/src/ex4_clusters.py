#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from npac import args
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import lib_fits
import lib_background
import lib_conv
import lib_cluster

def main():
    """ Exercise 4: Clusters """

    lib_fits.init()
    print(lib_fits.file_name)
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    thres = lib_background.threshold(pixels)

    peaks = lib_conv.complete_peaks_search(pixels)
    lums = lib_cluster.peak_lum(pixels, peaks)


    clusters = []
    for i in range(len(peaks)):
        clusters.append(lib_cluster.build_cluster(pixels, peaks[i], thres))

    signature_fmt_1 = 'RESULT: clusters_number={:d}'.format(len(clusters))
    signature_fmt_2 = 'RESULT: cluster_max_top={:d}'.format(max(lums))

    print(signature_fmt_1)
    print(signature_fmt_2)

    sort_clus = lib_cluster.sort_clusters(clusters, pixels)

    bcfe = sort_clus[0]

    fig, main_axes = plt.subplots()
    main_axes.imshow(pixels)

    for i in range(len(clusters)):
        xleft = clusters[i].coord[0]-clusters[i].ext
        xright =  clusters[i].coord[0] + clusters[i].ext
        ybottom = clusters[i].coord[1]-clusters[i].ext
        ytop = clusters[i].coord[1] + clusters[i].ext
        squarex = [xleft, xright, xright, xleft, xleft]
        squarey = [ybottom, ybottom, ytop, ytop, ybottom]
        plt.plot(squarex, squarey, 'r--')

    plt.show()



    signature_fmt_3 = 'RESULT: cluster_max_integral={:d}'.format(bcfe.lum)
    signature_fmt_4 = 'RESULT: cluster_max_column={:d}'.format(bcfe.coord[1])
    signature_fmt_5 = 'RESULT: cluster_max_row={:d}'.format(bcfe.coord[0])
    signature_fmt_6 = 'RESULT: cluster_max_extension={:d}'.format(bcfe.ext)

    print(signature_fmt_3)
    print(signature_fmt_4)
    print(signature_fmt_5)
    print(signature_fmt_6)



    return 0


if __name__ == '__main__':
    """ Execute exercise 3 """
    sys.exit(main())
