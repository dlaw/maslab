import flood_fill
import numpy as np
import profile

data = np.load("flood_fill_data.npy")

def main():
    d = data.copy()
    flood_fill.flood_fill(d)

profile.run('main()')

