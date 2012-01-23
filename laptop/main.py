#!/usr/bin/python2.7

import time, cv, numpy as np, arduino, kinect
from states import *

# wait for arduino and kinect to power up
time.sleep(1)

assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"

print("ready to go: waiting for switch")
while not arduino.get_switch():
    time.sleep(.02) # check every 20 ms

stop_time = time.time() + 180
arduino.set_helix(True)
state = FieldBounce()
while time.time() < stop_time:
    kinect.process_frame()
    new_state = state.next()
    if state.__class__ != new_state.__class__:
        print(new_state.__class__)
    state = new_state
arduino.set_helix(False)

print("finished: main.py exiting")
