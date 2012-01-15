#!/usr/bin/python2.7

"""
Simple code to test the Kinect's LED indicator and tilt functionality by
randomly changing their values every 3 seconds.

The recommended way to run from the command-line is:
    python tilt.py 2>/dev/null
If you don't pipe errors to /dev/null, your screen will quickly fill with lots
of camera errors. If you receive any errors, talk to jhurwitz. You're probably
missing some important library, or maybe you've misconfigured something.
"""

import freenect
import time
import random
import signal

keep_running = True
last_time = 0

def body(dev, ctx):
    global last_time
    if not keep_running: #we shouldn't still be running
        raise freenect.Kill
    if time.time() - last_time < 3: #only run every 3 secs
        return
    last_time = time.time()
    led = random.randint(0, 6)
    tilt = random.randint(-30, 30)
    freenect.set_led(dev, led)
    freenect.set_tilt_degs(dev, tilt)
    print('led[%d] tilt[%d] accel[%s]' % (led, tilt, freenect.get_accel(dev)))

"""If we don't have empty callbacks, weird bugs arise"""
def depth(dev, data, timestamp):
    return

def video(dev, data, timestamp):
    return

"""Called when the program quits via Ctrl-C"""
def handler(signum, frame):
    global keep_running
    keep_running = False

print('Press Ctrl-C in terminal to stop')
signal.signal(signal.SIGINT, handler)
freenect.runloop(body=body, depth=depth, video=video)

