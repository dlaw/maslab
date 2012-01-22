#!/usr/bin/python2.7

import time, cv, numpy as np, arduino, kinect
from states import *

time.sleep(1)
assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"
print("ready to go: waiting for switch")

while not arduino.get_switch():
    time.sleep(.05)

stop_time = time.time() + 180
state = FieldBounce()
while time.time() < stop_time:
    kinect.process_frame()
    new_state = state.next()
    if state.__class__ != new_state.__class__:
        print(new_state.__class__)
    state = new_state
