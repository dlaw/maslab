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
arduino.set_sucker(True)
state = FieldBounce()
print(state.__class__)
last_change = time.time()
while time.time() < stop_time - 40: #use last 40 secs for dump
    kinect.process_frame()
    try:
        new_state = state.next()
        assert new_state is not None
    except Exception, e:
        print(e)
        new_state = state
    if (state.timeout is not None) and (time.time() > last_change + state.timeout):
        new_state = FieldBounce()
    if state != new_state:
        try:
            state.finish()
        except Exception, e:
            print(e)
        last_change = time.time()
        print(new_state.__class__)
        state = new_state
print("transitioning to dump mode")
state = FieldBounce(want_dump = True)
while time.time() < stop_time:
    kinect.process_frame()
    try:
        state = state.next()
    except Exception, e:
        print(e)
arduino.set_speeds(0, 0) #just in case
arduino.set_sucker(False)
arduino.set_helix(False)

print("finished: main.py exiting")
