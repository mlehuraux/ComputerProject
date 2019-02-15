# -*- coding: utf-8 -*-
from npac import stars
from npac import coordinates


def conversion(i, j, pixels):
    """
    Convert coordinates from 2d array (i,j) into spatial coordinates (x,y).
    """
    x = j
    y = i
    return(x,y)

def get_radec(i,j, header, pixels):
    """
    Obtain radec coordinates from spatial coordinates (x,y).
    """

    my_wcs = coordinates.get_wcs(header)
    x = conversion(i,j, pixels)[0]
    y = conversion(i,j, pixels)[1]
    radec = coordinates.xy_to_radec(my_wcs, coordinates.PixelXY(x,y))
    return(radec)

def cluster_radec(clusters, i, header, pixels):
    """
    Take a cluster and extract radec coordinates from 2d array coordinates (i,j).
    """

    cluster_radec = get_radec(clusters[i].coord[0], clusters[i].coord[1], header, pixels)

    signature_fmt_1 = 'RESULT: right_ascension_{:02d} = {:.3f}'.format(i, cluster_radec[0])
    signature_fmt_2 = 'RESULT: declination_{:02d} = {:.3f}'.format(i, cluster_radec[1])

    print(signature_fmt_1)
    print(signature_fmt_2)
    return(cluster_radec)

def celestial_objects(cluster_radec, i):
    """
    Extract celestial objects in cluster
    """

    celestial_objects = stars.get_celestial_objects(cluster_radec)

    # Loop over all celestial objects in one cluster.
    for j in range(len(celestial_objects[0])):
        signature_fmt_3 = 'RESULT: celestial_object_{:02d}_{:02d} = {:s}'.format(i, j, list(celestial_objects[0].keys())[j])
        print(signature_fmt_3)

    return(0)