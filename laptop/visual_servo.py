import arduino, freenect, cv, frame_convert, numpy

freenect.sync_get_video()[0]

freenect.sync_get_depth()[0]


accum_err = 0
last = 0
def visual_servo(theta, kp=.5, ki=0, kd=0):
    accum_err += theta
    p, i, d, last = theta, accum_err, theta - last, theta
    turn = kp*p + ki*i + kd*d
    arduino.set_motors(.3 + turn, -(.3 - turn)) # R is reversed in hardware
