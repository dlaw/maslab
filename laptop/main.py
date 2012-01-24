#!/usr/bin/python2.7

import time, cv, numpy as np, arduino, kinect, states, signal

# wait for arduino and kinect to power up
time.sleep(1)

assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"

print("ready to go: waiting for switch")
while not arduino.get_switch():
    time.sleep(.02) # check every 20 ms

def kill_handler(signum, frame):
    arduino.set_speeds(0, 0)
    arduino.set_sucker(False)
    arduino.set_helix(False)
    exit()
signal.signal(signal.SIGINT, kill_handler)

stop_time = time.time() + 180
state = states.LookAround()

arduino.set_helix(True)
arduino.set_sucker(True)

while time.time() < stop_time:
    kinect.process_frame()
    try:
        new_state = state.next(stop_time - time.time())
        assert new_state is not None
    except Exception, e:
        print("{0} while attempting to change states".format(e))
        new_state = state
    if state != new_state:
        print("{0} with {1} seconds to go".format(new_state, stop_time - time.time()))
        state = new_state

arduino.set_speeds(0, 0) # just in case
arduino.set_sucker(False)
arduino.set_helix(False)

print("finished: main.py exiting")
