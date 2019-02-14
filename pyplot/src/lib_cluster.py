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
    pass

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
    avg = threshold+1
    integ0 = pixels[i][j]

    while avg > threshold :
        subimage = pixels[i-r:i+r+1, j-r:j+r+1]
        # Compute the pixel sum
        integ = np.sum(subimage) - integ0
        # Average
        avg = np.float(integ)/(npix_r(r)-npix_r(r-1))
        print(integ, avg, (npix_r(r)-npix_r(r-1)))
        integ0 = integ
        r+=1
    if r-1<1 :
        print("Cluster rejected")
    else :
        C = Cluster()
        C.coord = [i, j]
        C.lum = lum(pixels, r-1, i, j)
        C.ext = r-1
    #fmt(C)

    return(C)

def sort_clusters(clusters, pixels):

    sorted_clusters = [clusters[0]]
    sorted_lums = [clusters[0].lum]

    for i in range(1,len(clusters)):
        if clusters[i].lum < sorted_clusters[i-1].lum :
            sorted_clusters.append(clusters[i])
        else :
            j = i
            while clusters[i].lum >= sorted_clusters[j-1].lum and j>1:
                j-=1
            if clusters[i].lum == sorted_clusters[j-1].lum :
                if pixels[clusters[i].coord[0]][clusters[i].coord[1]] < pixels[sorted_clusters[j-1].coord[0]][sorted_clusters[j-1].coord[1]] :
                     sorted_clusters.insert(j-1, clusters[i])
                     sorted_lums.insert(j-1, clusters[i].lum)
                else :
                    k = j-1
                    while pixels[clusters[i].coord[0]][clusters[i].coord[1]] >= pixels[sorted_clusters[k-1].coord[0]][sorted_clusters[k-1].coord[1]] and k>1: :
                        k-=1
                    sorted_clusters.insert(k-1, clusters[i])
                    sorted_lums.insert(k-1, clusters[i].lum)
            else :
                sorted_clusters.insert(j-1, clusters[i])
                sorted_lums.insert(j-1, clusters[i].lum)







    return(sorted_clusters)
