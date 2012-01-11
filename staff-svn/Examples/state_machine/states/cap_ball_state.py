from istate import IState
from datetime import datetime
import explore_state

class CapBallState(IState):
    def __init__(self, sm, start_time):
        self.sm = sm
        self.start_time = start_time
    def next_state(self):
        if datetime.now() > self.start_time + 5:
            self.sm.motors.stop_capture_ball()
            return explore_state.ExploreState(self.sm)
        else:
            self.sm.motors.capture_ball()
            return self
