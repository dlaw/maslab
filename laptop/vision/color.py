#!/usr/bin/env python

import numpy

def select(hsv, targets, scalers):
    """
    targets = [target_hue, target_sat, target_val]
    scalers = [hue_c, sat_c, val_c]
    
    Returns points in hsv for which the distance between
    (hue / hue_c, sat / sat_c, val / val_c) and
    (target_hue / hue_c, target_sat / sat_c, target_val / val_c)
    is less than one.
    """
    hsv = hsv.astype('float64') - targets
    hsv[...,0] = ((hsv[...,0] + 90) % 180) - 90 # circular distance
    return numpy.sum(numpy.square(hsv / scalers), -1) < 1
