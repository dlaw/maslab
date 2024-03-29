#!/usr/bin/python2.7

import signal, time, arduino, kinect, navigation, maneuvering, sys, traceback, constants

time.sleep(1) # wait for arduino and kinect to power up

want_change = True

def run():
    global want_change
    print("starting state_tester.py")
    state = navigation.LookAround()
    arduino.set_helix(True)
    arduino.set_sucker(True)
    stop_time = time.time() + 180
    timeout_time = time.time() + state.timeout
    while time.time() < stop_time:
        if want_change:
            want_change = False
            arduino.drive(0, 0)
            print "Enter a state constructor (with no spaces) and, optionally, a time left (separated by a space), or enter nothing to quit"
            s = raw_input("> ")
            if s == "":
                kill()
            s = s.split(" ")
            if len(s) > 1:
                stop_time = time.time() + int(s[1])
            new_state = None
            for class_name in ["navigation", "maneuvering"]:
                try:
                    new_state = eval(class_name + "." + s[0])
                    break
                except AttributeError:
                    continue
            if new_state is None:
                print("{0} was not found in any of the classes".format(s[0]))
            else:
                state = new_state
                timeout_time = time.time() + state.timeout
                print("State manually changed to {0}".format(state))
        kinect.process_frame()
        try:
            new_state = (state.on_timeout() if time.time() > timeout_time
                                             else state.next(stop_time - time.time()))
            if new_state is not None: # if the state has changed
                state = new_state
                timeout_time = time.time() + state.timeout
                print("{0} with {1} seconds to go".format(state, stop_time - time.time()))
        except Exception, ex:
            print("{0} while attempting to change states".format(ex))
            traceback.print_exc(file=sys.stdout)

def change_state(*args):
    global want_change
    want_change = True

signal.signal(signal.SIGINT, change_state)
                
def kill():
    arduino.drive(0, 0)
    arduino.set_sucker(False)
    arduino.set_helix(False)
    arduino.set_door(False)
    exit()

if __name__ == '__main__': # called from the command line
    run()
    kill()

