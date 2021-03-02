import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
import matplotlib.widgets as widgets
import os
import sys
import warnings

warnings.filterwarnings("ignore")

path = 'C:/Users/novar/Downloads/Research Stuff/Jupyter Notebooks/Data Exports/Ranges/OSM_export_all_'
dist_min = 50
dist_max = 300
step_size = 5

distances = np.arange(dist_min, dist_max + step_size, step_size)

data_path = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]

while True:

    dataframe = pd.DataFrame()

    print('Your options are: \n')
    for area in area_names:
        print(area)

    area = input('\nChoose your area: ')

    area = [i for i in area_names if i.startswith(area)][0]

    record_min = 1
    for dist in distances:
        datapath = path + str(dist) + '.csv'
        temp_frame = pd.read_csv(datapath)
        temp_frame = temp_frame[area][1:]
        min = temp_frame.min()
        dataframe[str(dist)] = temp_frame
        if min < record_min:
            record_min = min

    def get_data(chosen_dist):
        y = dataframe[str(chosen_dist)].to_list()
        return(y)

    fig, ax = plt.subplots(figsize=(7, 5))

    fig.subplots_adjust(bottom=0.2, top=0.75)
    x = np.arange(1, 41)

    data = dataframe.transpose()
    data = data.to_numpy()

    line = ax.loglog(x, data[0, :], color='k', lw=2)[0]
    ax.set(xlim=(0, 40), ylim=(record_min, 1.01), title=area)
    ax.tick_params(labelsize=14)
    plt.ylabel('s (Normalized Size)', size=14)
    plt.xlabel('k (Ordinal Rank by Size)', size=14)

    ax_dist = fig.add_axes([0.3, 0.85, 0.4, 0.05])
    ax_dist.spines['top'].set_visible(True)
    ax_dist.spines['right'].set_visible(True)

    s_dist = widgets.Slider(
                    ax=ax_dist,
                    label='Distance (ft) ',
                    valmin=distances[0],
                    valmax=distances[-1],
                    valfmt='%i ft',
                    facecolor='#cc7000',
                    valstep=step_size
                   )

    def update(val):
        dist = s_dist.val
        line.set_data(x, get_data(dist))
        fig.canvas.draw_idle()

    s_dist.on_changed(update)

    plt.show()

    while True:
        answer = str(input('\nGet another area? [y/n]: '))
        if answer in ('y', 'n'):
            break
        print("invalid input.")
    if answer == 'y':
        continue
    else:
        print("\nThanks for using this tool!")
        break
