import arduino, kinect, random

class State:
    # override next() whenever an action should not be interrupted
    def next(self, dump_mode=False):
        """
        Superclass method to execute appropriate event handlers and actions.
        Returns a new state if the state shall change, and self otherwise.
        """
        if (any(arduino.get_stall()) or any(arduino.get_bump())
            or max(arduino.get_ir() > 1)):
            return self.on_stuck()
        elif dump_mode and kinect.yellow_walls:
            return self.on_yellow()
        elif not dump_mode and kinect.balls:
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

class GoToBall(State):
    def on_ball(self):
        # drive
    def default_action(self):
        # lost the ball
        return LookAround()

class SnarfBall(State):
    # override next() in this one, because we don't know if a ball is present
    # TODO learn to snarf balls that are up against the wall

class GoToYellow(State):
    def on_yellow(self):
        pass
    def default_action(self):
        # lost the wall
        return LookAround()

class DumpBalls(State):
    # override next() in this one

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
