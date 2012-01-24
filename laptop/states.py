import arduino, kinect, random, time, constants

class State:
    # override next() whenever an action should not be interrupted
    def next(self, time_left):
        """
        Superclass method to execute appropriate event handlers and actions.
        Returns a new state if the state shall change, and self otherwise.
        """
        if (any(arduino.get_stall()) or any(arduino.get_bump())
            or max(arduino.get_ir() > 1)):
            return self.on_stuck()
        elif time_left < constants.dump_search and kinect.yellow_walls:
            return self.on_yellow()
        elif time_left >= constants.dump_search and kinect.balls:
            return self.on_ball()
        else:
            return state.default_action()
    def on_ball(self):
        """
        Action to take when a ball is seen and dump_mode is False.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToBall()
    def on_yellow(self):
        """
        Action to take when a yellow wall is seen and dump_mode is True.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToYellow()
    def on_stuck(self):
        """
        Action to take when we are probably stuck.
        Returns a new state if the state shall change, and self otherwise.
        """
        return Unstick()
    def default_action(self):
        """
        Action to take if none of the other event handlers apply.
        Returns a new state if the state shall change, and self otherwise.
        """
        raise NotImplementedError # subclass has to do this one

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
        # TODO do the right thing for balls against a wall
        if time.time() < self.stop_time:
            arduino.drive(constants.snarf_speed, 0)
            return self
        else:
            return LookAround()

class GoToYellow(State):
    def on_yellow(self):
        # drive towards the yellow
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.wall_follow_kp * (wall['col'][0] - 80)
        # slow down if you need to turn more, but never go backwards
        arduino.drive(max(0, .8-abs(offset)), offset)
        return self
    def default_action(self):
        # lost the wall
        return LookAround()

class DumpBalls(State):
    def next(self, time_left): # override next so nothing can interrupt a dump
        # TODO drive towards the wall
        arduino.set_door(True)
        if time_left < constants.dump_dance:
            return self
        else:
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
    # override next() in this one

class GoToWall(State):
    # Drive straight to a wall, then enter state FollowWall

class FollowWall(State):
    def __init__(self, side, distance):
        pass
    def on_ball():
        # if a wall is in the way, ignore the ball
    def on_yellow():
        # if a wall is in the way, ignore the yellow
    def default_action(self):
        pass
