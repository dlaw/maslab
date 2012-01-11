import unittest
from Maslab.Staff.Examples.state_machine import state_machine
from Maslab.Staff.Examples.state_machine.states import *
from Maslab.Staff.Examples.actuators import dummy_motors
from Maslab.Staff.Examples.sensors import vision

class TestSM(unittest.TestCase):
    def setUp(self):
        self.sm = state_machine.StateMachine()
        # We're going to simulate ball detection, so replace the
        # detect_balls method with a dummy method.
        self.sm.vis.detect_balls = lambda: None
        # Make sure the motors don't actually turn by using
        # the dummy motor module
        self.sm.motors = dummy_motors
    def test_explore_transition(self):
        # Simulate Ball Detection
        self.sm.vis.ball_locs = [vision.BallPosition(1,0)]
        expected = to_ball_state.ToBallState
        actual = explore_state.ExploreState(self.sm).next_state()
        self.assertIsInstance(actual, expected,
                              msg='ExploreState transition to ToBallState incorrect.')
    def test_to_ball_transitions(self):
        # Simulate close ball Detection
        self.sm.vis.ball_locs = [vision.BallPosition(1,0)]
        expected = cap_ball_state.CapBallState
        actual = to_ball_state.ToBallState(self.sm).next_state()
        self.assertIsInstance(actual, expected,
                              msg='ToBallState transition to CapBallState incorrect.')
        # Simulate loss of ball
        self.sm.vis.ball_locs = []
        expected = explore_state.ExploreState
        actual = to_ball_state.ToBallState(self.sm).next_state()
        self.assertIsInstance(actual, expected,
                              msg='ToBallState transition to ExploreState incorrect.')

if __name__ == '__main__':
    unittest.main()
