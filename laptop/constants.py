# Ball dumping: timing of the end
dump_start = 30 # seconds before end-of-match to start looking for yellow wall
dump_dance = 5 # seconds before end-of-match to start the HappyDance
dance_turn = 0.4 # the speed at which to turn while dancing
dance_period = 0.2 # how often to switch dance directions

drive_speed = 1 # standard drive forward speed
ball_follow_kp = .004
close_ball_row = 80 # snarf the ball if its center is below this row
wall_follow_kp = .004

# Ball snarfing: when we consume a ball
snarf_time = .7 # how long to snarf a ball after losing sight of it
snarf_speed = 1 # how fast to drive while snarfing
