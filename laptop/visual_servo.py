import arduino
import numpy as np
import freenect
import cv
from vision import color, blobs
import time

accum_err = 0
last = 0
speed = 0.25
def visual_servo(theta, kp=-.001, ki=0, kd=0):
    global accum_err, last
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    left = np.clip(2*speed + turn, -1, 1)
    right = np.clip(2*speed - turn, -1, 1)
    arduino.set_motors(left, -right) # R is reversed in hardware



while True:
    raw_image = freenect.sync_get_video()[0]
    image = numpy.empty((240,320,3), 'uint8')
    cv.Resize(cv.fromarray(raw_image), cv.fromarray(image))
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    depth = freenect.sync_get_depth()[0].astype('float32')
    good = color.select(image, [175,255,255], [30,150,250]).astype('uint32')
    blob_data = blobs.find_blobs(good, depth, 1000, 30000)

    # select the blob with the largest size
    # (there should be very few, so we can be slow)
    biggest = None
    theta = None
    for size, blob_color, (avg_r, var_r), (avg_c, var_c), (avg_d, var_d) in blob_data:
        if biggest is None or size > biggest:
            biggest = size
            theta = 320 - avg_c
    if theta is None:
        accum_err = 0
        last = 0
        arduino.set_motors(speed, speed)
    else:
        visual_servo(theta)
    time.sleep(.05)
