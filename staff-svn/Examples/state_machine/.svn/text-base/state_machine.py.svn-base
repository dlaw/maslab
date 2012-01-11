import Maslab
from states import *
from Maslab.Staff.Examples.sensors import vision
from Maslab.Staff.Examples.actuators import dummy_motors

class StateMachine:
    def __init__(self):
        self.vis = vision.Vision()
        self.motors = dummy_motors
    def runSM(self):
        self.state = explore_state.ExploreState(self)
        while True:
            self.vis.detect_balls()
            self.state = self.state.next_state()

if __name__ == '__main__':
    sm = StateMachine()
    sm.runSM()
