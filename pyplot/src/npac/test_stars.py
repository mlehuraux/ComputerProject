#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from npac.stars import *
import sys

class RaDec:
    """Spatial coordinates."""

    def __init__(self):
        """ Initializing """
        self.ra = 0.0
        self.dec = 0.0

radec = RaDec()
radec.ra, radec.dec = 1.0, 1.0
cobjects, out, _ = get_celestial_objects(radec, 0.1)
for cobj_name in cobjects:
    print(cobj_name,cobjects[cobj_name])
sys.exit(0)

