#import arduino, freenect, cv, frame_convert, numpy
import freenect, cv, frame_convert, numpy
import vision.blob_select as blob_select

def track_ball():
    global accum_err, last
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
        turn = numpy.random.rand(1)[0]
        arduino.set_motors(.3 + turn, -(.3 - turn))
    else:
        visual_servo(320-avg_c)

accum_err = 0
last = 0
def visual_servo(theta, kp=.5, ki=0, kd=0):
    global accum_err, last
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    arduino.set_motors(.3 + turn, -(.3 - turn)) # R is reversed in hardware
