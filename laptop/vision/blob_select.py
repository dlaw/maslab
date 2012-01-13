import cv
import numpy as np
import blobs
import hue_select

def blob_select(rgb, depth, target_hue, hue_tolerance, sat_val_tolerance, sat_c, val_c, min_blob_area, max_blob_area):
    filtered = hue_select.hue_select(rgb, target_hue, hue_tolerance, sat_val_tolerance, sat_c, val_c).astype(np.uint32)
    blob_data = blobs.find_blobs(filtered, depth, min_blob_area, max_blob_area)
    # no extra filtering for now (but we might want to add more later, based on depth variance, etc.)
    return blob_data, filtered

