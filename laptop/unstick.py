import numpy as np, constants, random, time, arduino, states

class Unstick(states.State):
    def __init__(self):
        triggered_bump = np.where(arduino.get_bump())[0]
        triggered_ir = np.where(np.array(arduino.get_ir()) > constants.ir_stuck_threshold)[0]
        if len(triggered_bump) and (not len(triggered_ir) or np.random.rand()<constants.probability_to_use_bump):
            # only bump sensors are triggered, or both types are triggered and we randomly chose to look at bump
            choice = random.choice(triggered_bump)
            self.trigger_released = lambda: return (not arduino.get_bump()[choice])
            self.escape_angle = constants.bump_sensor_angles[choice] # randomly pick a triggered bump sensor
        elif len(triggered_ir):
            # only IR senors are triggered, or both types are triggered and we randomly chose to look at IR
            choice = random.choice(triggered_ir)
            self.trigger_released = lambda: return (arduino.get_ir()[choice] < constants.ir_unstuck_threshold)
            self.escape_angle = constants.ir_sensor_angles[choice] # randomly pick a triggered IR sensor
        else:
            self.escape_angle = None # oops, not good style
        self.unstick_complete = False
        self.reverse = False
        self.last_change = time.time()
    def next(self, time_left):
        if self.escape_angle is None: # init said nothing was triggered
            return states.LookAround()
        if self.unstick_complete:
            if time.time() > self.last_change + constants.unstick_clean_period:
                return states.LookAround()
        elif self.trigger_released():
            self.unstick_complete = True
            self.reverse = False
            self.last_change = time.time()
        elif time.time() > self.last_change + constants.unstick_wiggle_period[self.reverse]:
            self.reverse = not self.reverse
            self.last_change = time.time()
        self.drive_away()
    def drive_away(self):
        """
        We're hitting an obstacle at angle (front of the robot is 0, positive
        is clockwise) and need to escape. Periodically reverse the direction
        (as determined by self.reverse).

        For angles 0 or pi, you want full forward and no turn. For angles pi/2
        and 3pi/2, you want no forward and only turn. This suggests using trig
        functions, though maybe there's a better implementation.
        """
        offset = np.pi if self.reverse else 0
        drive = constants.escape_drive_kp * np.cos(self.escape_angle + offset)
        turn = constants.escape_turn_kp * np.sin(self.escape_angle + offset)
        arduino.drive(drive, turn)
