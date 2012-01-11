class BallPosition:
    """Location of a single ball."""
    # angle of ball relative to the camera,
    # in radians. + is right, - is left
    angle = None
    # distance in cm, from camera to the ball
    distance = None
    def __init__(self, dist, ang):
        self.distance = dist
        self.angle = ang

class Vision:
    """Vision processing."""
    # List of BallPosition objects from nearest
    # to furthest. [] if no balls are detected
    ball_locs = []
    # Get an image from the camera, process it,
    # and update ball_locs
    def detect_balls(self):
        pass
