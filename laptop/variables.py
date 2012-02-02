import time

number_possessed_balls = 0 # how many balls we currently possess in our "extra cheese" (third) level
go_to_ball_attempts = 0 # how many times we've tried to get a ball since a new ball has entered the third level
stalking_yellow = False # when we're stalking yellow, we can't follow walls
time_last_seen_yellow = time.time()

