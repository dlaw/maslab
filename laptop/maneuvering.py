import numpy as np, constants, random, time, arduino, main, navigation

class SnarfBall(main.State):
    timeout = constants.snarf_time
    def next(self, time_left): # override next because we snarf no matter what
        arduino.drive(constants.snarf_speed, 0)

class DumpBalls(main.State):
    timeout = constants.dump_search # don't time out!
    def next(self, time_left): # override next so nothing can interrupt a dump
        fl, fr = arduino.get_ir()[1:-1]
        if min(fl, fr) > constants.dump_ir_final:
            arduino.drive(0, 0)
            if time_left < constants.dump_dance:
                arduino.set_door(True)
                return HappyDance()
        elif abs(fl - fr) > constants.dump_ir_turn_tol:
            arduino.drive(0, np.sign(fr - fl) * constants.dump_turn_speed)
        else:
            arduino.drive(constants.dump_fwd_speed, 0)

class HappyDance(main.State): # dead-end state
    timeout = constants.dump_dance # don't time out! (keep this in case we ever increase dump_dance)
    def __init__(self):
        self.next_shake = time.time() + constants.dance_period
        self.shake_dir = 1
    def next(self, time_left): # override next so nothing can interrupt a HappyDance
        if time.time() > self.next_shake:
            self.next_shake = time.time() + constants.dance_period
            self.shake_dir *= -1
        arduino.drive(0, self.shake_dir * constants.dance_turn)

class Unstick(main.State):
    def __init__(self):
        triggered_bump = np.where(arduino.get_bump())[0]
        triggered_ir = np.where(np.array(arduino.get_ir()) > constants.ir_stuck_threshold)[0]
        if len(triggered_bump) and (not len(triggered_ir) or np.random.rand()<constants.probability_to_use_bump):
            # only bump sensors are triggered, or both types are triggered and we randomly chose to look at bump
            choice = random.choice(triggered_bump)
            self.trigger_released = lambda: (not arduino.get_bump()[choice])
            self.escape_angle = constants.bump_sensor_angles[choice] # randomly pick a triggered bump sensor
        elif len(triggered_ir):
            # only IR senors are triggered, or both types are triggered and we randomly chose to look at IR
            choice = random.choice(triggered_ir)
            self.trigger_released = lambda: (arduino.get_ir()[choice] < constants.ir_unstuck_threshold)
            self.escape_angle = constants.ir_sensor_angles[choice] # randomly pick a triggered IR sensor
        else:
            self.escape_angle = None # oops, not good style
        if self.escape_angle is not None:
            self.escape_angle += random.uniform(-constants.unstick_angle_offset_range, constants.unstick_angle_offset_range) # add some randomness
            self.unstick_complete = False
            self.stop_time = time.time() + constants.unstick_wiggle_period
    def next(self, time_left):
        if self.escape_angle is None: # init said nothing was triggered
            return HerpDerp()
        if self.unstick_complete:
            if time.time() > self.stop_time:
                return navigation.LookAround() # this is intentionally not a HerpDerp!
        elif self.trigger_released():
            self.unstick_complete = True
            self.stop_time = time.time() + constants.unstick_clean_period
        elif time.time() > self.stop_time:
            return Unstick()
        self.drive_away()
    def drive_away(self):
        """
        We're hitting an obstacle at angle (front of the robot is 0, positive
        is clockwise) and need to escape. Periodically reverse the direction
        (as determined by self.reverse).

        For angles 0 or pi, you want full forward and no turn. For angles pi/2
        and 3pi/2, you want no forward and only turn. This suggests using trig
        functions, though maybe there's a better implementation.

        Note that escape_angle is the angle of the sensor, but the trig
        functions rely on having the angle you want to drive, so add pi.
        """
        drive = np.cos(self.escape_angle + np.pi)
        turn = np.sin(self.escape_angle + np.pi)
        arduino.drive(drive, turn)

class HerpDerp(main.State):
    timeout = constants.herp_derp_timeout
    def __init__(self):
        self.drive = -1 * random.uniform(constants.herp_derp_min_drive,
                                         constants.herp_derp_max_drive)
        self.turn = (np.sign(arduino.get_ir()[2] - arduino.get_ir()[1]) *
                     random.uniform(constants.herp_derp_min_turn,
                                    constants.herp_derp_max_turn))
    def next(self, time_left): # don't do anything else
        arduino.drive(self.drive, self.turn)
    def on_timeout(self):
        return navigation.LookAround()

