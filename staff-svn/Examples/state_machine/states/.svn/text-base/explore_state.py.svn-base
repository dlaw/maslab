from istate import IState
import to_ball_state

class ExploreState(IState):
    def __init__(self, sm):
        self.sm = sm
    def next_state(self):
        if self.sm.vis.ball_locs != []:
            return to_ball_state.ToBallState(self.sm)
        else:
            self.sm.motors.rotate_left()
            return self
