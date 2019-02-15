#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import lib_fits
import lib_cluster
import lib_stars

def main():
    """ Exercise 6: Display stars """

    lib_fits.init()
    print(lib_fits.file_name)
    global pixels
    global header
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    clusters = lib_cluster.find_clusters(pixels)

    for i in range(6):
        rad = lib_stars.cluster_radec(clusters, i, header, pixels)
        lib_stars.celestial_objects(rad, i)
    return 0

if __name__ == '__main__':
    """ Execute exercise 5 """
    sys.exit(main())
