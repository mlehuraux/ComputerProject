#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from args import *
import sys, os

arg0, arg1 = get_args()
datapath = os.environ['DATAPATH']
print(arg0.replace(datapath,'$DATAPATH'),arg1)

sys.exit(0)

