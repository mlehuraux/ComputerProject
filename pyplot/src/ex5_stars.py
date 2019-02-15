#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from npac import stars
import lib_fits
import lib_cluster
import lib_stars


def main():
    """ Exercise 5: Stars """

    lib_fits.init()
    print(lib_fits.file_name)
    global pixels
    global header
    header, pixels = lib_fits.read_first_image(lib_fits.file_name)

    clusters = lib_cluster.find_clusters(pixels)

    clusters_radec = []
    for i in range(len(clusters)):
        clusters_radec.append(lib_stars.get_radec(clusters[i].coord[0], clusters[i].coord[1], header, pixels))


    signature_fmt_1 = 'RESULT: right_ascension = {:.3f}'.format(clusters_radec[0][0])
    signature_fmt_2 = 'RESULT: declination = {:.3f}'.format(clusters_radec[0][1])

    print(signature_fmt_1)
    print(signature_fmt_2)

    celestial_objects = stars.get_celestial_objects(clusters_radec[0])
    #print(celestial_objects)

    for i in range(len(celestial_objects[0])):
        signature_fmt_3 = 'RESULT: celestial_object_{:02d} = {:s}'.format(i, list(celestial_objects[0].keys())[i])
        signature_fmt_4 = 'RESULT: dist_{:02d} = {:5.1f}'.format(i, list(celestial_objects[0].values())[i])
        print(signature_fmt_3)
        print(signature_fmt_4)


    return 0

if __name__ == '__main__':
    """ Execute exercise 4 """
    sys.exit(main())
