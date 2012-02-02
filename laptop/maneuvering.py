import numpy as np, constants, random, time, arduino, main, navigation, variables

class SnarfBall(main.State):
    timeout = constants.snarf_time
    def next(self, time_left): # override next because we snarf no matter what
        arduino.drive(constants.snarf_speed, 0)

class DumpBalls(main.State):
    timeout = constants.dump_time # don't time out!
    def __init__(self, final = False):
        self.final = final
    def next(self, time_left): # override next so nothing can interrupt a dump
        fl, fr = arduino.get_ir()[1:-1]
        if min(fl, fr) > constants.dump_ir_final:
            arduino.drive(0, 0)
            if not self.final:
                return ConfirmLinedUp()
            else:
                return WaitInSilence()
        elif abs(fl - fr) > constants.dump_ir_turn_tol:
            arduino.drive(0, np.sign(fr - fl) * constants.dump_turn_speed)
        else:
            arduino.drive(constants.dump_fwd_speed, 0)

class WaitInSilence(main.State):
    timeout = constants.dump_time # don't time out!
    def __init__(self):
        arduino.set_helix(False)
        arduino.set_sucker(False)
        variables.helix_enabled = False
    def next(self, time_left):
        arduino.drive(0, 0)
        if time_left < constants.eject_time:
            return HappyDance()

class ConfirmLinedUp(main.State):
    timeout = constants.back_up_time
    def next(self, time_left):
        arduino.drive(-constants.dump_fwd_speed, 0)
    def on_timeout(self):
        return navigation.GoToYellow()

class HappyDance(main.State): # dead-end state
    timeout = constants.eject_time
    def __init__(self):
        self.next_shake = time.time() + constants.dance_period
        self.shake_dir = 1
    def next(self, time_left): # override next so nothing can interrupt a HappyDance
        arduino.set_door(True)
        if time.time() > self.next_shake:
            self.next_shake = time.time() + constants.dance_period
            self.shake_dir *= -1
        arduino.drive(0, self.shake_dir * constants.dance_turn)
    def on_timeout(self):
        arduino.set_door(False)
        variables.number_possessed_balls = 0 # we no longer possess any balls
        return navigation.LookAround()

class Unstick(main.State):
    def __init__(self):
        variables.ball_attempts += 1
        triggered_bump = np.where(arduino.get_bump())[0]
        triggered_ir = np.where(np.array(arduino.get_ir()) > constants.ir_stuck_threshold)[0]
        if (np.random.rand() < constants.probability_to_use_bump
            or not len(triggered_ir)) and len(triggered_bump):
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
            self.escape_angle += random.triangular(-constants.unstick_angle_offset_range, constants.unstick_angle_offset_range) # add some randomness
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
        turn = constants.unstick_max_turn * np.sin(self.escape_angle + np.pi)
        arduino.drive(drive, turn)

class HerpDerp(main.State):
    timeout = 2*constants.herp_derp_timeout
    def __init__(self):
        self.drive = -1 * random.uniform(constants.herp_derp_min_drive,
                                         constants.herp_derp_max_drive)
        if arduino.get_bump()[1]:
            self.sign = 1
        elif arduino.get_bump()[0]:
            self.sign = -1
        else:
            self.sign = np.sign(arduino.get_ir()[2] - arduino.get_ir()[1])
        self.turn = random.uniform(constants.herp_derp_min_turn,
                                   constants.herp_derp_max_turn)
        self.midtime = time.time() + constants.herp_derp_timeout
    def next(self, time_left): # don't do anything else
        if time.time() < self.midtime:
            arduino.drive(self.drive, self.sign*self.turn)
        else:
            arduino.drive(self.drive, -1*self.sign*self.turn)

