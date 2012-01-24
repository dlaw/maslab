import arduino, kinect

# We allow multiple state transitions per frame (e.g. LookAround -> GoToBall -> BallSnarf)
# However, default_action is always the last state transition.
# Ideally, State.on_*() changes state without taking action,
# and State.act() takes an action.

class State:
    def next(state, dump_mode=False): # first param is intentionally not "self"
        """
        Superclass method to execute appropriate event handlers and actions.
        Returns a new state if the state shall change, and self otherwise.
        """
        if dump_mode:
            if kinect.yellow_walls:
                state = state.on_yellow(kinect.yellow_walls)
        else:
            if kinect.balls:
                state = state.on_ball(kinect.balls)
        if stalled motor or IR too close or bump sensor triggered:
            state = state.on_stuck()
        return state.act()
    def on_ball(self, balls):
        """
        Action to take when a ball is seen and dump_mode is False.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToBall()
    def on_yellow(self, yellow_walls):
        """
        Action to take when a yellow wall is seen and dump_mode is True.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToYellow()
    def on_stuck(self, params?):
        """
        Action to take when we are probably stuck.
        Returns a new state if the state shall changem and self otherwise.
        """
        return Unstick()

class GoToBall(State):
    def on_ball(self, balls):
        pass

class GoToYellow(State):
    def on_yellow(self, yellow_walls):
        pass

class Unstick(State):
    def on_stuck(self, params?):
        pass
