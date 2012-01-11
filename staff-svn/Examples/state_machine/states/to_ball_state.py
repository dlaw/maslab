from istate import IState
from datetime import datetime
import cap_ball_state
import explore_state

class ToBallState(IState):
    def __init__(self, sm):
        self.sm = sm
    def next_state(self):
        if self.sm.vis.ball_locs == []:
            return explore_state.ExploreState(self.sm)
        elif self.sm.vis.ball_locs[0].distance < 10.0:
            return cap_ball_state.CapBallState(self.sm, datetime.now())
        else:
            self.sm.motors.move_forward(self.sm.vis.ball_locs[0].angle)
            return self
