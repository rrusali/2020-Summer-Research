import freud
import numpy as np
import pandas as pd
import os

name_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI))]

def getAverageHexOrder(filepath, k=2):
    # Reformat the file into a numpy array
    N = int(np.genfromtxt(filepath, max_rows=1))
    try:
        positions = np.genfromtxt(filepath, skip_header=2, invalid_raise=False)[:, 1:4].reshape(-1, N, 3)
        # Remove a dimension
        positions = positions[0]

        # Find the x and y lengths of our box
        xmin = positions[0][0]
        xmax = xmin
        ymin = positions[0][1]
        ymax = ymin

        for i in range(N):

            x = positions[i][0]
            y = positions[i][1]
            positions[i][2] = 0

            if x < xmin: xmin = x
            elif x > xmax: xmax = x

            if y < ymin: ymin = y
            elif y > ymax: ymax = y

        Lx = xmax - xmin
        Ly = ymax - ymin

        # Compute our Hexatic order
        op = freud.order.Hexatic(k=k)
        op.compute(system = ({'Lx': Lx, 'Ly': Ly, 'dimensions': 2}, positions))

        # Return the average
        return np.average(np.absolute(op.particle_order))

    except:
        print(filepath)

for name in area_names:
    print('Now working on: ' + name)
    data_path = '%s/%s/%s_building_coords_reformatted.txt' % (name_path, name, name)
    hex_val = getAverageHexOrder(data_path)
    save_path = '%s/%s/%s_2hex_order.txt' % (name_path, name, name)
    with open(save_path, 'w+') as f:
        f.write(str(hex_val))
