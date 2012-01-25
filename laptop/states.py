import arduino, kinect, random, time, constants, numpy as np, unstick, navigation

# TODO how to deliberately lose sight of a ball? either for balls
# against a wall or for partially obstructed balls.

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
        return unstick.Unstick()
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
        return navigation.GoToWall() # enter wall-following mode

class GoToBall(State):
    def on_ball(self):
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
