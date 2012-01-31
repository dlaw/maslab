#!/usr/bin/python2.7

import signal, time, arduino, kinect, constants

time.sleep(1) # wait for arduino and kinect to power up
assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"

class State:
    timeout = 10 # default timeout of 10 seconds per state
    def next(self, time_left):
        """Superclass method to execute appropriate event handlers and actions."""
        if any(arduino.get_bump()) or max(arduino.get_ir()) > 1:
            return self.on_stuck()
        elif time_left < constants.dump_search and kinect.yellow_walls:
            return self.on_yellow()
        elif time_left >= constants.dump_search and kinect.balls:
            return self.on_ball()
        return self.default_action()
    def on_ball(self): # called by State.next if applicable
        """Action to take when a ball is seen and we're not in dump mode."""
        import navigation
        return navigation.GoToBall()
    def on_yellow(self): # called by State.next if applicable
        """Action to take when a yellow wall is seen and we're in dump mode."""
        import navigation
        return navigation.GoToYellow()
    def on_stuck(self): # called by State.next if applicable
        """Action to take when we are probably stuck."""
        import maneuvering
        return maneuvering.Unstick()
    def default_action(self): # called by State.next if applicable
        """Action to take if none of the other event handlers apply."""
        raise NotImplementedError # subclass has to do this one
    def on_timeout(self): # called by main.py if applicable
        """Action to take once self.timeout has passed.""" 
        import maneuvering
        return maneuvering.HerpDerp()

def run(duration = 180):
    import navigation
    print("ready to go: waiting for switch")
    while not arduino.get_switch():
        time.sleep(.02) # check every 20 ms
    stop_time = time.time() + duration
    state = navigation.LookAround()
    timeout_time = time.time() + state.timeout
    arduino.set_helix(True)
    arduino.set_sucker(True)
    while time.time() < stop_time:
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

def kill(*args):
    arduino.drive(0, 0)
    arduino.set_sucker(False)
    arduino.set_helix(False)
    arduino.set_door(False)
    exit()

signal.signal(signal.SIGINT, kill)

if __name__ == '__main__': # called from the command line
    run()
    kill()

