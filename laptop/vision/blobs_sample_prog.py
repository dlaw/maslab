import pyximport
pyximport.install()

import blobs
import numpy as np
import profile

data = np.load("blobs_sample_data.npy")
depth = np.load("blobs_sample_depth.npy")
def main():
    blobs.find_blobs(data, depth, min_size=100, max_size=1000)

profile.run('main()')

