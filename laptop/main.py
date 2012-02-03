#!/usr/bin/python2.7

import signal, time, arduino, kinect, constants, variables, random

time.sleep(1) # wait for arduino and kinect to power up
assert arduino.is_alive(), "could not talk to Arduino"
assert arduino.get_voltage() > 8, "battery not present or voltage low"
assert kinect.initialized, "kinect not initialized"

class State:
    timeout = 10 # default timeout of 10 seconds per state
    def next(self, time_left):
        """Superclass method to execute appropriate event handlers and actions."""
        if any(arduino.get_bump()[0:2]):
            return self.on_block()
        elif any(arduino.get_bump()[2:4]) or max(arduino.get_ir()) > 1:
            return self.on_stuck()
        elif time_left < constants.dump_time and kinect.yellow_walls:
            return self.on_yellow()
        elif (time_left >= constants.dump_time and kinect.balls
              and not variables.ignore_balls
              and not variables.ignore_balls_until_yellow):
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
    def on_block(self): # called by State.next if applicable
        """Action to take when we are blocked (sensed by a high front touch sensor)."""
        import maneuvering
        return maneuvering.HerpDerp()
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
    print("ready to go: waiting for switch")
    arduino.set_led(True)
    initial_switch = arduino.get_switch()
    while arduino.get_switch() == initial_switch:
        time.sleep(.02) # check every 20 ms
    arduino.set_led(False)
    stop_time = time.time() + duration
    state = navigation.LookAround()
    timeout_time = time.time() + state.timeout
    variables.helix_enabled = True
    helix_on = True
    next_helix_twiddle = duration - constants.helix_twiddle_period[not helix_on]
    arduino.set_helix(True)
    arduino.set_sucker(True)
    time.sleep(.3)
    while time.time() < stop_time:
        kinect.process_frame()
        time_left = stop_time - time.time()

        try: # sometimes this throws a NoneType exception, so let's catch it to be safe
            new_balls = arduino.get_new_ball_count()
        except Exception, ex:
            new_balls = 0
            print("{0} while attempting to get new ball count".format(ex))
        variables.number_possessed_balls += new_balls
        if new_balls:
            print("{0} NEW BALLS, now {1} balls total with {2} seconds to go".format(new_balls, variables.number_possessed_balls, time_left))
            variables.ball_attempts = 0
        
        if not variables.ignore_balls and variables.ball_attempts >= constants.max_ball_attempts:
            variables.ignore_balls = True
            end_ignore_balls = time_left - random.uniform(.5, 1)*constants.ignore_balls_length
            variables.ball_attempts = 0
        if variables.ignore_balls and time_left < end_ignore_balls:
            variables.ignore_balls = False
        if kinect.yellow_walls:
            variables.ignore_balls_until_yellow = False
        if variables.number_possessed_balls >= constants.max_balls_to_possess:
            variables.helix_enabled = False
            arduino.set_helix(False) # possess future balls in the lower level
        if variables.helix_enabled and time_left < next_helix_twiddle:
            helix_on = not helix_on
            arduino.set_helix(helix_on)
            next_helix_twiddle = time_left - constants.helix_twiddle_period[not helix_on]

        variables.yellow_stalk_period = (time_left < constants.yellow_stalk_time)
        if (variables.yellow_stalk_period and # we're near the end
            kinect.yellow_walls and # and we can see a yellow wall
            variables.number_possessed_balls > constants.min_balls_to_stalk_yellow): # and the third level is sufficiently full
            variables.can_follow_walls = False
        
        try:
            new_state = (state.on_timeout() if time.time() > timeout_time
                         else state.next(time_left))
            if new_state is not None: # if the state has changed
                state = new_state
                timeout_time = time.time() + state.timeout
                # TODO remove the {2} attempts
                print("{0} with {1} seconds to go, ({2}, {3}, {4})".format(state, time_left, variables.ball_attempts, variables.can_follow_walls, variables.ignore_balls))
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

