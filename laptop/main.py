#!/usr/bin/python2.7

import time, cv, numpy as np, arduino, kinect, states

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
state = states.FieldBounce()
print(state)
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
        if isinstance(state, states.FieldBounce):
            new_state = states.Explore()
        else:
            new_state = states.Reverse()
    if state != new_state:
        try:
            state.finish()
        except Exception, e:
            print(e)
        last_change = time.time()
        print("{0} with {1} seconds to go".format(new_state, stop_time - time.time()))
        state = new_state
print("transitioning to dump mode")
state = states.FieldBounce()
states.want_dump = True
while time.time() < stop_time:
    kinect.process_frame()
    try:
        new_state = state.next()
        assert new_state is not None
    except Exception, e:
        print(e)
    if state != new_state:
        try:
            state.finish()
        except Exception, e:
            print(e)
        last_change = time.time()
        print("{0} with {1} seconds to go".format(new_state, stop_time - time.time()))
        state = new_state
arduino.set_speeds(0, 0) #just in case
arduino.set_sucker(False)
arduino.set_helix(False)

print("finished: main.py exiting")
