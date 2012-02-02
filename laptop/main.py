#!/usr/bin/python2.7

import signal, time, arduino, kinect, constants

time.sleep(1) # wait for arduino and kinect to power up
assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"

# runtime variables used by multiple states
number_possessed_balls = 0 # how many balls we currently possess in our "extra cheese" (third) level
ball_attempts = 0 # how many times we've tried to get a ball since a new ball has entered the third level
stalking_yellow = False # when we're stalking yellow, we can't follow walls
time_last_seen_yellow = time.time()

class State:
    timeout = 10 # default timeout of 10 seconds per state
    def next(self, time_left):
        """Superclass method to execute appropriate event handlers and actions."""
        if any(arduino.get_bump()) or max(arduino.get_ir()) > 1:
            return self.on_stuck()
        elif time_left < constants.dump_time and kinect.yellow_walls:
            return self.on_yellow()
        elif time_left >= constants.dump_time and kinect.balls:
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
        import navigation
        return navigation.LookAround()

def run(duration = 180):
    import navigation
    global number_possessed_balls, ball_attempts, stalking_yellow, time_last_seen_yellow

    print("ready to go: waiting for switch")
    initial_switch = arduino.get_switch()
    while arduino.get_switch() == initial_switch:
        time.sleep(.02) # check every 20 ms
    stop_time = time.time() + duration
    state = navigation.LookAround()
    timeout_time = time.time() + state.timeout
    arduino.set_helix(True)
    arduino.set_sucker(True)
    while time.time() < stop_time:
        kinect.process_frame()
        time_left = stop_time - time.time()

        new_balls = arduino.get_new_ball_count()
        number_possessed_balls += new_balls
        if new_balls:
            print("{0} NEW BALLS, now {1} balls total".format(new_balls, number_possessed_balls))
            ball_attempts = 0
        
        if number_possessed_balls >= constants.max_balls_to_possess:
            arduino.set_helix(False) # possess future balls in the lower level
        if (number_possessed_balls >= constants.min_balls_to_stalk_yellow and
            time_left < constants.yellow_stalk_time and
            kinect.yellow_walls):
            stalking_yellow = True
        if kinect.yellow_walls:
            time_last_seen_yellow = time.time()
        if (time_left < constants.dump_time and
            time.time() - time_last_seen_yellow > constants.allowable_time_without_yellow_while_stalking):
            stalking_yellow = False
        
        try:
            new_state = (state.on_timeout() if time.time() > timeout_time
                         else state.next(time_left))
            if new_state is not None: # if the state has changed
                state = new_state
                timeout_time = time.time() + state.timeout
                print("{0} with {1} seconds to go".format(state, time_left))
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

