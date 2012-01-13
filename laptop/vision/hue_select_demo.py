#!/usr/bin/env python
import hue_select
import freenect
import cv
import frame_convert
import numpy as np

current_hue = 0
threshold = 10
max_sq_dist_from_true = 450000
sat_const = 10
val_const = 10

def change_hue(value):
    global current_hue
    current_hue = value

def change_threshold(value):
    global threshold
    threshold = value

def change_max_dist(value):
    global max_sq_dist_from_true
    max_sq_dist_from_true = value

def change_sat_const(value):
    global sat_const
    sat_const = value

def change_val_const(value):
    global val_const
    val_const = value

def show_hue():
    rgb = freenect.sync_get_video()[0]
    filtered = hue_select.hue_select(rgb, target_hue = current_hue, hue_tolerance = threshold, sat_val_tolerance = max_sq_dist_from_true, sat_c = 0.1*sat_const, val_c = 0.1*val_const)
    mask = np.array([current_hue, 255, 255])
    #multiply by hsv to get original colors, or by mask to get current_hue 
    colored = filtered[:,:,np.newaxis] * mask
    colored = colored.astype(np.uint8)
    display = colored.copy()
    cv.CvtColor(cv.fromarray(colored), cv.fromarray(display), cv.CV_HSV2BGR)
    cv.ShowImage('Hue', cv.fromarray(display))

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))

cv.NamedWindow('Hue')
cv.NamedWindow('Video')
cv.CreateTrackbar('Target hue (0-180)', 'Hue', current_hue, 180, change_hue)
cv.CreateTrackbar('Hue tolerance (+/-)', 'Hue', threshold, 90, change_threshold)
cv.CreateTrackbar('Max squared distance from true color', 'Hue', max_sq_dist_from_true, 1000000, change_max_dist)
cv.CreateTrackbar('Saturation constant (x10)', 'Hue', sat_const, 30, change_sat_const)
cv.CreateTrackbar('Value constant (x10)', 'Hue', val_const, 30, change_val_const)

print('Press ESC in window to stop')

while 1:
    show_hue()
    show_video()
    if cv.WaitKey(10) == 27:
        break

