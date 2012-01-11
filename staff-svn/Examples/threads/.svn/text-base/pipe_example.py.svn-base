from multiprocessing import Process, Pipe
import time

class Vision:
    ball_locs = []
    def detect_balls(self):
        # Fake say a ball was detected
        self.ball_locs = ['ball detected!']
        
def run(vis, pipe):
    while True:
        vis.detect_balls()
        # Check to see if something's been requested
        if pipe.poll(0):
            #pipe.recv()
            pipe.send(vis.ball_locs)
            # Sleep for a bit, then terminate
            time.sleep(1)
            break

if __name__ == '__main__':
    vis = Vision()
    parent_conn, child_conn = Pipe()
    p1 = Process(target=run,args=(vis,child_conn))
    print 'spawing child process'
    p1.start()
    # Request the ball locations
    print 'requesting ball locations'
    parent_conn.send(True)
    # Print the result
    print parent_conn.recv()
    # Wait for the vision code to end
    print 'Waiting for child to terminate.'
    p1.join()
    print 'Terminated'
