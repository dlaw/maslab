import arduino, kinect, random, time, constants, numpy as np
from unstick import Unstick

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
    timeout = constants.look_around_timeout
    def __init__(self):
        self.turn = random.choice([-1, 1]) * constants.look_around_speed
    def default_action(self):
        arduino.drive(0, self.turn)
    def on_timeout(self):
        return GoToWall()

class GoToBall(State):
    def on_ball(self): # TODO do the right thing if we're getting close to a wall
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = constants.ball_follow_kp * (ball['col'][0] - 80)
        arduino.drive(max(0, .8 - abs(offset)), offset)
        if ball['row'][0] > constants.close_ball_row:
            return SnarfBall()
    def default_action(self):
        return LookAround()

class SnarfBall(State):
    timeout = constants.snarf_time
    def next(self, time_left): # override next because we snarf no matter what
        arduino.drive(constants.snarf_speed, 0)
    def on_timeout(self):
        return LookAround() # lost the wall

class GoToYellow(State):
    def on_yellow(self):
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.yellow_follow_kp * (wall['col'][0] - 80)
        arduino.drive(max(0, .8 - abs(offset)), offset)
    def default_action(self):
        return LookAround() # lost the wall

class DumpBalls(State):
    def next(self, time_left): # override next so nothing can interrupt a dump
        # TODO drive towards the wall
        if time_left > constants.dump_dance:
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


class GoToWall(State):
    # Drive straight to a wall, then enter state FollowWall
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        arduino.drive(constants.drive_speed, 0)

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
