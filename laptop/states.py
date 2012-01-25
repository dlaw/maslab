import arduino, kinect, random, time, constants, numpy as np

# TODO how to lose sight of a ball? either for balls against a wall or
# for partially obstructed balls.

class State:
    def next(self, time_left):
        """Superclass method to execute appropriate event handlers and actions."""
        if any(arduino.get_bump()) or max(arduino.get_ir()) > 1:
            return self.on_stuck()
        elif time_left < constants.dump_search and kinect.yellow_walls:
            return self.on_yellow()
        elif time_left >= constants.dump_search and kinect.balls:
            return self.on_ball()
        else:
            return state.default_action()
    def on_ball(self):
        """Action to take when a ball is seen and dump_mode is False."""
        return GoToBall()
    def on_yellow(self):
        """Action to take when a yellow wall is seen and dump_mode is True."""
        return GoToYellow()
    def on_stuck(self):
        """Action to take when we are probably stuck."""
        return Unstick()
    def default_action(self):
        """Action to take if none of the other event handlers apply."""
        raise NotImplementedError # subclass has to do this one
    def on_timeout(self):
        """Action to take once self.timeout has passed.""" # called by main.py
        return LookAround()

class LookAround(State):
    def __init__(self):
        arduino.rotate(random.choice([6.29, -6.29])) # 2 pi in either direction
    def default_action(self):
        if arduino.get_angle() == 0: # saw nothing after turning
            return GoToWall() # drive to wall and then enter wall following mode
        else:
            return self

class GoToBall(State):
    def on_ball(self): # TODO do the right thing if we're getting close to a wall
        # drive towards the ball
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = constants.ball_follow_kp * (ball['col'][0] - 80)
        # slow down if you need to turn more, but never go backwards
        arduino.drive(max(0, .8-abs(offset)), offset)
        if ball['row'][0] > constants.close_ball_row:
            return SnarfBall()
        return self
    def default_action(self):
        # lost the ball
        return LookAround()

class SnarfBall(State):
    def __init__(self):
        self.stop_time = time.time() + constants.snarf_time
    def next(self, time_left): # override next because we snarf no matter what
        if time.time() < self.stop_time:
            arduino.drive(constants.snarf_speed, 0)
            return self
        else:
            return LookAround()

class GoToYellow(State):
    def on_yellow(self):
        # drive towards the yellow
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.yellow_follow_kp * (wall['col'][0] - 80)
        # slow down if you need to turn more, but never go backwards
        arduino.drive(max(0, .8-abs(offset)), offset)
        return self
    def default_action(self):
        # lost the wall
        return LookAround()

class DumpBalls(State):
    def next(self, time_left): # override next so nothing can interrupt a dump
        # TODO drive towards the wall
        if time_left < constants.dump_dance:
            return self
        else:
            arduino.set_door(True)
            return HappyDance()

class HappyDance(State):
    def __init__(self):
        self.next_shake = time.time() + constants.dance_period
        self.shake_dir = 1
    def next(self, time_left): # override next so nothing can interrupt a HappyDance
        if time.time() > self.next_shake:
            self.next_shake = time.time() + constants.dance_period
            self.shake_dir *= -1
        arudino.drive(0, self.shake_dir * constants.dance_turn)
        return self

class Unstick(State):
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
            return LookAround()
        if self.unstick_complete:
            if time.time() > self.last_change + constants.unstick_clean_period:
                return LookAround()
        elif self.trigger_released():
            self.unstick_complete = True
            self.reverse = False
            self.last_change = time.time()
        elif time.time() > self.last_change + constants.unstick_wiggle_period[self.reverse]:
            self.reverse = not self.reverse
            self.last_change = time.time()
        self.drive_away()
        return self
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

class GoToWall(State):
    # Drive straight to a wall, then enter state FollowWall
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        else:
            arduino.drive(constants.drive_speed, 0)
            return self

class FollowWall(State):
    def __init__(self, on_left = None):
        self.on_left = random.choice([True, False]) if on_left is None else on_left
        self.ir = 0 if self.on_left else 3
        self.dir = -1 if self.on_left else 1 # sign of direction to turn into wall
        self.time_wall_seen = time.time()
        self.time_look_away = time.time() + constants.wall_follow_time
    def default_action(self):
        dist = arduino.get_ir()[self.ir]
        if time.time() > self.time_look_away:
            return LookAway(self.on_left)
        elif dist > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            arduino.drive(constants.drive_speed, constants.wall_follow_kp *
                          self.dir * (constants.wall_follow_dist - dist))
        elif time.time() - self.time_wall_seen < constants.wall_follow_timeout:
            arduino.drive(0, constants.wall_follow_turn * self.dir)
        else: # lost wall
            return LookAround()
