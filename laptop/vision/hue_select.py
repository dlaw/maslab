#!/usr/bin/env python
import cv
import numpy as np

def hue_select(rgb, target_hue, hue_tolerance, sat_val_tolerance, sat_c, val_c):
    hsv = rgb.copy()
    cv.CvtColor(cv.fromarray(rgb), cv.fromarray(hsv), cv.CV_RGB2HSV)
    hue = hsv[:,:,0]
    hue = hue.astype(np.int16) #to prevent overflow error
    differences = np.mod(hue - target_hue, 180)
    filtered = np.logical_or(
                  differences <= hue_tolerance,
                  differences >= 180-hue_tolerance
               )
    sat = (255-hsv[:,:,1]).astype(np.uint32)
    val = (255-hsv[:,:,2]).astype(np.uint32)
    sv_filter = (sat_c*np.square(sat) + val_c*np.square(val)) < sat_val_tolerance
    filtered = filtered * sv_filter
    return filtered

