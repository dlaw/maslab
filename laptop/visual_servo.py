import arduino
import numpy as np
import freenect
import vision.blob_select as blob_select
import cv
import color

accum_err = 0
last = 0
def visual_servo(theta, kp=-.002, ki=0, kd=0):
    global accum_err, last
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    arduino.set_motors(np.clip(.5 + turn, -1, 1), np.clip(-(.5 - turn), -1, 1)) # R is reversed in hardware

while True:
    image = freenect.sync_get_video()[0]
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    depth = freenect.sync_get_depth()[0].astype('float32')
    good = color.select(image, [175,255,255], [30,150,250]).astype('uint32')
    blob_data = blobs.find_blobs(good, depth, 200, 30000)
    
    # select the blob with the largest size
    # (there should be very few, so we can be slow)
    biggest = None
    biggest_idx = None
    for idx, (colors, size, avg_r, avg_c, avg_d, var_d) in enumerate(blob_data):
        if biggest is None or size > biggest:
            biggest = size
            biggest_idx = idx
    if biggest is None:
        accum_err = 0
        last = 0
        arduino.set_motors(.5, .5)
    else:
        visual_servo(320-avg_c)

