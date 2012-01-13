import arduino
import numpy as np
import freenect
import vision.blob_select as blob_select

accum_err = 0
last = 0
def visual_servo(theta, kp=-.002, ki=0, kd=0):
    global accum_err, last
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    arduino.set_motors(np.clip(.5 + turn, -1, 1), np.clip(-(.5 - turn), -1, 1)) # R is reversed in hardware

while True:
    rgb = freenect.sync_get_video()[0]
    depth = freenect.sync_get_depth()[0].astype('float32')
    blob_data, filtered = blob_select.blob_select(rgb, depth, target_hue = 0, hue_tolerance = 10, sat_val_tolerance = 45000, sat_c = 1.2, val_c = 0.8, min_blob_area = 1000, max_blob_area = 35000)
    # select the blob with the largest size
    # (there should be very few, so we can be slow)
    biggest = None
    biggest_idx = None
    for idx, (colors, size, avg_r, avg_c, avg_d, var_d) in enumerate(blob_data):
        if biggest is None or size > biggest:
            biggest = size
            biggest_idx = idx
    if biggest is None: #move randomly
        accum_err = 0
        last = 0
        arduino.set_motors(.5, .5)
    else:
        visual_servo(320-avg_c)

