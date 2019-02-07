#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from npac.pixels import *
import sys

ps = PixelsSet()

# x,y
# 1,3  2,3  3,3
# 1,2  2,2  3,2
#      2,1  3,1

# val
# 10   20   20
# 10   20   20
#      10   10

ps.add(2, 1, 10)
ps.add(3, 1, 10)
ps.add(1, 2, 10)
ps.add(2, 2, 20)
ps.add(3, 2, 20)
ps.add(1, 3, 10)
ps.add(2, 3, 20)
ps.add(3, 3, 20)

print("center: {:.2f} {:.2f}".format(*ps.get_center()))
print("centroid: {:.2f} {:.2f}".format(*ps.get_centroid()))
print("weighted: {:.2f} {:.2f}".format(*ps.get_weighted_centroid()))
print("peak: {:.2f} {:.2f}".format(*ps.get_peak()))

sys.exit(0)

