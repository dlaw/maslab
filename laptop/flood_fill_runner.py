import flood_fill
import numpy as np
import profile

data = np.load("flood_fill_data.npy")
data_list = [data.copy() for i in range(100)]

def main():
    for d in data_list:
        flood_fill.flood_fill(d)

profile.run('main()')

