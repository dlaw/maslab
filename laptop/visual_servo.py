#!/usr/bin/python2.7

import arduino, freenect, cv
import numpy as np
import freenect
from vision import color, blobs, kinect
import time

accum_err = 0
last = 0
speed = 0.4
def visual_servo(theta, kp=-.003, ki=0, kd=0):
    global accum_err, last
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    left = np.clip(speed + turn, -1, 1)
    right = np.clip(speed - turn, -1, 1)
    arduino.set_motors(-left, right) # R is reversed in hardware

while True:
    # TODO get image from kinect.  broken.
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    depth = freenect.sync_get_depth()[0].astype('float32')
    good = color.select(image, [175,255,255], [15,150,250]).astype('uint32')
    blob_data = blobs.find_blobs(good, depth, 26)
    # select the blob with the largest size
    # (there should be very few, so we can be slow)
    biggest = None
    theta = None
    for size, blob_color, (avg_r, var_r), (avg_c, var_c), (avg_d, var_d) in blob_data:
        if biggest is None or size > biggest:
            biggest = size
            theta = 160 - avg_c
    if theta is None:
        accum_err = 0
        last = 0
        arduino.set_motors(speed, speed)
    else:
        visual_servo(theta)
