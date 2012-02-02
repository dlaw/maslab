import constants

number_possessed_balls = 0 # how many balls we currently possess in our "extra cheese" (third) level
go_to_ball_attempts = 0 # how many times we've tried to get a ball since a new ball has entered the third level
can_follow_walls = True # can we follow walls? (set to False to stay near yellow)
ignore_balls = False
saw_yellow = [False for i in range(constants.max_look_around_timeouts)]
yellow_stalk_period = False

