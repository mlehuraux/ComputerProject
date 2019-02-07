#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from npac.coordinates import *
import sys

class FakeWcs():
    """Fake WCS.

    Just swapps first and second coordinates. This avoid the need
    for a real fits image so to test our two functions.
    """
    def __init__(self):
        """Initialization"""
        self.fake_coef = 1.0

    def wcs_pix2world(self, x_y, fake):
        """Fake pixel coordinates to world coordinates transformation"""
        return (x_y[0][1] * self.fake_coef, x_y[0][0] * self.fake_coef),

    def wcs_world2pix(self, radec, fake):
        """Fake world coordinates to pixel coordinates transformation"""
        return (
            radec[0][1] * self.fake_coef,
            radec[0][0] * self.fake_coef),

wcs = FakeWcs()
pxy = PixelXY(1, 2)
radec = RaDec(2, 1)
print(xy_to_radec(wcs, pxy) == radec)
print(radec_to_xy(wcs, radec) == pxy)

sys.exit(0)

