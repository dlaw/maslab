import arduino, kinect

class State:
    # override next() whenever an action should not be interrupted
    def next(self, dump_mode=False):
        """
        Superclass method to execute appropriate event handlers and actions.
        Returns a new state if the state shall change, and self otherwise.
        """
        if (any(arduino.get_stall()) or any(arduino.get_bump())
            or max(arduino.get_ir()) > 1):
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
    def on_ir(self):
        """
        Action to take when we are probably stuck.
        Returns a new state if the state shall change, and self otherwise.
        """
        return FollowWall()
    def default_action(self):
        """
        Action to take if none of the other event handlers apply.
        Returns a new state if the state shall change, and self otherwise.
        """
        raise NotImplementedError # subclass has to do this one

class LookAround(State):
    def default_action(self):
        pass # turn 360 degrees, then enter state GoToWall

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
    # TODO don't go directly to balls/walls if there is a wall in the way
    def default_action(self): pass
