# -*- coding: utf-8 -*-
import sys
from npac import args
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as scp
import lib_background
import lib_conv


class Cluster(object):
    """ Define a class for cluster object
    Characteristics :
        - pixel coordinates of the peak
        - integral
        - extension
    """
    def ___init___(self,coord, lum, ext):
        self.coord = coord
        self.lum = lum
        self.ext = ext
        self.lumpeak = lumpeak

def fmt(C):
    print("Cluster coordinates : {} \nCluster luminosity :  {} \nCluster extension : {}".format(C.coord, C.lum, C.ext))
    return 0

def npix_r(r):
    return((2*r+1)**2)

def lum(pixels, r, i, j):
    l = 0
    for p in range(i-r,i+r+1):
        for q in range(j-r, j+r+1):
            l+=pixels[max(0, min(p, len(pixels)-1))][max(0, min(q, len(pixels[0])-1))]
    return(l)

def peak_lum(pixels, peaks):
    lums=[]
    for i in range(len(peaks)):
        lums.append(pixels[peaks[i][0]][peaks[i][1]])
    return(lums)

def build_cluster(pixels, peak, threshold):

    # Extract sub image
    i = peak[0]
    j = peak[1]

    r = 1
    avg = pixels[i][j]
    integ0 = pixels[i][j]

    while avg > threshold :
        subimage = pixels[max(0, i-r): min(i+r+1, len(pixels)), max(0, j-r):min(j+r+1, len(pixels[0]))]
        # Compute the pixel sum
        integ = np.sum(subimage) - integ0
        # Average
        avg = np.float(integ)/(npix_r(r)-npix_r(r-1))
        #print(r, integ, integ0, avg - threshold, threshold, (npix_r(r)-npix_r(r-1)))
        integ0 = np.sum(subimage)
        r+=1
    if r-2<1 :
        print("Cluster rejected")
        return
    else :
        C = Cluster()
        C.coord = [i, j]
        C.lum = lum(pixels, r-2, i, j)
        C.ext = r-2
        C.lumpeak = pixels[i][j]
        #fmt(C)

        return(C)

def sort_clusters(clusters, pixels):

    sorted_clusters = sorted(clusters, key=lambda cluster: cluster.lum, reverse=True)
    test = []

    for i in range(len(sorted_clusters)-2):
        begin = i
        end = i
        while sorted_clusters[i].lum == sorted_clusters[end+1].lum:
            end+=1
        sorted(clusters[begin:end+1], key=lambda cluster: cluster.lumpeak, reverse=True)
        test.append([sorted_clusters[i].lum, sorted_clusters[i].lumpeak])
    #print(test)
    return(sorted_clusters)


