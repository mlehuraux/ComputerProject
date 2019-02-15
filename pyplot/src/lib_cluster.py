# -*- coding: utf-8 -*-
import numpy as np
import lib_background
import lib_conv


class Cluster(object):
    """ Define a class for cluster object.
        Characteristics :
        - pixel coordinates of the peak,
        - integral,
        - extension,
        - luminosity of the peak.
    """

    def ___init___(self,coord, lum, ext, lumpeak):
        """
        Define cluster's parameters.
        """
        self.coord = coord
        self.lum = lum
        self.ext = ext
        self.lumpeak = lumpeak

def fmt(c):
    """
    Print cluster content of interest (without lumpeak).
    """
    print("Cluster coordinates : {} \nCluster luminosity :  {} \nCluster extension : {}".format(c.coord, c.lum, c.ext))
    return 0

def npix_r(r):
    """
    Pixels' number in a square of size (2*r+1).
    """
    return((2*r+1)**2)

def lum(pixels, r, i, j):
    """
    Compute the luminosity of a sub image, centre on a peak in (i,j) with a radius r.
    """
    lumi = 0

    # Loop over all pixels in a sub image and add its luminosity.
    for p in range(i-r,i+r+1):
        for q in range(j-r, j+r+1):
            lumi+=pixels[max(0, min(p, len(pixels)-1))][max(0, min(q, len(pixels[0])-1))]
    return(lumi)

def peak_lum(pixels, peaks):
    """
    Give the list of luminosities of peaks.
    """
    lums=[]
    for i in range(len(peaks)):
        lums.append(pixels[peaks[i][0]][peaks[i][1]])
    return(lums)

def build_cluster(pixels, peak, threshold):
    """
    For a given peak, try to build a cluster,
    take the average luminosity of surounded pixels and compare it with the threshold.
    It returns a cluster or a None if it does not exist.
    """
    # Extract sub image
    i = peak[0]
    j = peak[1]

    r = 1
    avg = pixels[i][j]
    integ0 = pixels[i][j]

    # loop to have the max radius of the cluster.
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

        return(C)

def sort_clusters(clusters):
    """
    Sort clusters by decreasing luminosity.
    If luminosity of two clusters are equal, we sort them with the peak luminosity.
    """


    sorted_clusters = sorted(clusters, key=lambda cluster: cluster.lum, reverse=True)
    # To print luminosities only to check the ordering process.
    test = []

    # loop over elements of sorted list.
    for i in range(len(sorted_clusters)-2):
        begin = i
        end = i
        while sorted_clusters[i].lum == sorted_clusters[end+1].lum:
            end+=1
        sorted(clusters[begin:end+1], key=lambda cluster: cluster.lumpeak, reverse=True)
        test.append([sorted_clusters[i].lum, sorted_clusters[i].lumpeak])
    return(sorted_clusters)


def find_clusters(pixels):
    """
    From the array of pixels, retunrs directly the sorted list of clusters.
    Result of ex4.
    """

    threshold = lib_background.threshold(pixels)

    peaks = lib_conv.complete_peaks_search(pixels)

    clusters = []

    # Loop over all the peaks.
    for i in range(len(peaks)):
        clust = build_cluster(pixels, peaks[i], threshold)
        if clust == None :
            continue
        else :
            clusters.append(clust)

    sort_clus = sort_clusters(clusters)

    return(sort_clus)


