#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities for the world coordinate system
"""

import collections
import numpy as np
import warnings

from astropy.wcs import WCS
from astropy.io import fits
from astropy.io.fits.header import Header

warnings.filterwarnings('ignore', category=Warning, append=True)

# ======
# Coordinate systems - Use namedtuple as simple Class.
# * x/y position in an image : PixelXY(x,y)
# * ra/dec position in the sky : RaDec(ra,dec)
# =====
PixelXY = collections.namedtuple('PixelXY', ['x', 'y'])
RaDec = collections.namedtuple('RaDec', ['ra', 'dec'])


# ======
# Information for a given image
# =====

def get_wcs(fits_header: Header) -> WCS:
    """Parse the WCS keywords from a FITS image header

    Parameters
    ----------
    fits_header : astropy.io.fits.header.Header
        Header from a FITS HDU image

    Returns
    ----------
    out : instance of WCS class
        object performing standard WCS transformations.
        For more information see astropy.wcs.WCS

    Examples
    ----------
    Read default FITS

    FITS file path is defined in _test() function
    in order to be shared by all tests
    Open the FITS file
    >>> data = fits.open(fits_path)

    Take the header of the first HDU
    >>> header = data[0].header
    >>> assert(type(header) == Header)
    """
    return WCS(fits_header)


# =====
# Converters
# =====
def xy_to_radec(wcs_object: WCS, pxy: PixelXY) -> RaDec:
    """ Convert the x/y coordinates of an image pixel
    into the ra/dec coordinates of a celestial body

    Parameters
    ----------
    wcs_object: Instance of WCS
        a wcs object, as returned by get_wcs()
    pxy: an instance of PixelXY
        x/y position in an image (See definition above)

    Returns
    ----------
    out : an instance of RaDec
        ra/dec position in the sky for the pixel with coordinates (x, y).

    Examples
    ----------
    >>> pxy = PixelXY(0.0, 0.0)

    Open the FITS file, grab the header,
    and instantiate the WCS object
    FITS file path is defined in _test() function
    in order to be shared by all tests
    >>> data = fits.open(fits_path)
    >>> header = data[0].header
    >>> wcs_object = get_wcs(header)

    Compute the RA/Dec of the pixel
    >>> radec = xy_to_radec(wcs_object, pxy)
    >>> print(type(radec) == RaDec)
    True
    """
    pixel = np.array([[pxy.x, pxy.y], ], np.float_)
    sky = wcs_object.wcs_pix2world(pixel, 0)
    return RaDec(ra=sky[0][0], dec=sky[0][1])


def radec_to_xy(wcs_object: WCS, rd: RaDec) -> PixelXY:
    """ Convert the ra/dec coordinates of a celestial body
    into the x/y coordinates of an image pixel.

    Parameters
    ----------
    wcs_object: Instance of WCS
        a wcs object, as returned by get_wcs()
    rd : Instance of RaDec
        ra/dec position in the sky for a pixel, in degrees.
        Ra ranges from 0 to 360 degree.
        Dec ranges from 0 to 90 degree.

    Returns
    ----------
    out : Instance of PixelXL
        x/y position in the sky for a pixel with coordinates (ra/dec).

    Examples
    ----------
    Open the FITS file, grab the header,
    and instantiate the WCS object
    FITS file path is defined in _test() function
    in order to be shared by all tests
    >>> data = fits.open(fits_path)
    >>> header = data[0].header
    >>> wcs_object = get_wcs(header)

    Compute the RA/Dec of the pixel
    Ra/Dec in degrees.
    >>> ra = header['CRVAL1']
    >>> dec = header['CRVAL2']
    >>> radec = RaDec(ra, dec)
    >>> pxy = radec_to_xy(wcs_object, radec)
    >>> print(type(pxy) == PixelXY)
    True

    Print pixel position (x, y) as Integers
    >>> print(np.array(pxy, dtype=int))
    [736 806]
    """
    coord = np.array([[rd.ra, rd.dec], ], np.float_)
    result = wcs_object.wcs_world2pix(coord, 0)
    return PixelXY(x=result[0][0], y=result[0][1])

def _tests():
    """ Unit tests for coordinates.py To run the test, execute:

    python3 coordinates.py

    It should exit gracefully if no error (exit code 0),
    otherwise it will print on the screen the failure.

    In PyCharm, just click on Run "Doctests in coordinates" button (green button),
    or CTRL+click on the file, and choose Run "Doctests in coordinates".
    """
    import doctest

    # Add the FITS file path to the global variables in order to
    # be shared by all tests
    global_args = globals()
    global_args["fits_path"] = "../../../data/fits/common.fits"

    doctest.testmod(globs=global_args)

if __name__ == '__main__':
    """ Execute the test suite """
    _tests()
