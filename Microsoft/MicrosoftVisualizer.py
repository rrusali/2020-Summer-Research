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
from scipy.optimize import curve_fit
from uncertainties import ufloat
import matplotlib.image as mpimg
import re

warnings.filterwarnings("ignore")

path = 'C:/Users/novar/Downloads/Research Stuff/Jupyter Notebooks/Data Exports/Microsoft Ranges/Microsoft_export_all_'
dist_min = 100
dist_max = 1290
step_size = 5
points = 100

distances = np.arange(dist_min, dist_max + step_size, step_size)

data_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]
image_path = 'D:/Research Files/Clustering Images/'

while True:

    clicked = False
    previous_dist = 0

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
        temp_frame = temp_frame[area][1:points]
        min = temp_frame.min()
        dataframe[str(dist)] = temp_frame
        if min < record_min:
            record_min = min

    def get_data(chosen_dist):
        y = dataframe[str(chosen_dist)].to_list()
        return(y)

    fig, ax = plt.subplots(ncols=2, figsize=(20, 10))

    fig.subplots_adjust(bottom=0.2, top=0.75, hspace=0.4)
    x = [i for i in range(1, len(temp_frame) + 1)]

    data = dataframe.transpose()
    data = data.to_numpy()

    exp_plot = ax[0]
    img_plot = ax[1]
    exp_line_upper, = exp_plot.plot(x, x, lw = 2, c='pink', alpha=0)
    exp_line_lower, = exp_plot.plot(x, x, lw = 2, c='pink', alpha=0)
    exp_line, = exp_plot.plot(x, x, lw = 2, c='r', alpha=0)
    line = exp_plot.loglog(x, data[0, :], color='k', lw=2)[0]
    exp_plot.set(
                    xlim=(0, points),
                    ylim=(record_min, 1.01),
                    title=area,
                )
    exp_plot.set_xlabel('k (Ordinal Rank by Size)', fontsize=14)
    exp_plot.set_ylabel('s (Normalized Size)', fontsize=14)
    exp_plot.tick_params(labelsize=14)

    ax_dist = fig.add_axes([0.3, 0.85, 0.4, 0.05])
    ax_dist.spines['top'].set_visible(True)
    ax_dist.spines['right'].set_visible(True)

    # Code for the slider
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
        y = get_data(dist)
        line.set_data(x, y)

        global previous_dist
        ovito = ovito_coords(area, dist)
        image_folder = image_path + area + '/'
        current_dist = closest_range(image_folder, ovito)
        if current_dist != previous_dist:
            img = mpimg.imread(get_image(area, ovito))
            img_plot.clear()
            img_plot.axis('off')
            img_plot.imshow(img)
            scale = get_scale(data_path, area)
            img_plot.set(title='Clustering distance of: ' + str(int(current_dist * scale)) + ' ft')
            previous_dist = current_dist

        if clicked:
            exp_plot.collections.pop()
            new_y = [x for x in y if str(x) != 'nan']
            new_x = [i + 1 for i in range(len(new_y))]

            exp_y, y_lower, y_upper, label = get_bounds(new_x, new_y)
            exp_line.set_ydata(exp_y)
            exp_line_lower.set_ydata(y_lower)
            exp_line_upper.set_ydata(y_upper)

            exp_plot.fill_between(x, y_lower, y_upper, alpha=0.2, color='pink')
            exp_plot.legend(handles=[exp_line],labels=[str(label)], loc='lower left')

        fig.canvas.draw_idle()

    s_dist.on_changed(update)

    # Code for the button
    class Index(object):
        def next(self, event):
            global clicked
            clicked = not clicked
            if clicked:
                dist = s_dist.val
                y = get_data(dist)
                new_y = [x for x in y if str(x) != 'nan']
                new_x = [i + 1 for i in range(len(new_y))]

                exp_y, y_lower, y_upper, label = get_bounds(new_x, new_y)
                exp_line.set_ydata(exp_y)
                exp_line_lower.set_ydata(y_lower)
                exp_line_upper.set_ydata(y_upper)

                exp_plot.fill_between(x, y_lower, y_upper, alpha=0.2, color='pink')
                exp_line.set_alpha(1)
                exp_line_lower.set_alpha(1)
                exp_line_upper.set_alpha(1)
                exp_plot.legend(handles=[exp_line],labels=[str(label)], loc='lower left')
            else:
                exp_plot.collections.pop()
                exp_line.set_alpha(0)
                exp_line_lower.set_alpha(0)
                exp_line_upper.set_alpha(0)
                exp_plot.get_legend().remove()

    axnext = plt.axes([0.75, 0.04, 0.15, 0.08])
    bnext = widgets.Button(axnext, 'Show exp. line \nof best fit')
    bnext.label.set_fontsize(14)
    callback = Index()
    bnext.on_clicked(callback.next)

    def closest_range(image_folder, target):
        ranges = [float(f[:-4]) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
        ranges = np.asarray(ranges)
        idx = (np.abs(ranges - target)).argmin()
        return ranges[idx]

    def get_image(area_name, target):
        image_folder = image_path + area_name + '/'
        target = closest_range(image_folder, target)
        image = image_folder + str(target) + '.png'
        return(image)

    def get_scale(data_path, area_name):
        scale = 0
        openpath = data_path + area_name + '/' + area_name + '_scale.txt'

        with open(openpath) as f:
            f = f.read()
            scale = re.sub('[^0-9]', '', f)

        return float(scale)

    def get_bounds(new_x, new_y):
        variables, covariance = curve_fit(expFunc, new_x, new_y)
        exp_y = x**variables[0]
        sigma = np.sqrt(np.diagonal(covariance))
        label = ufloat(variables[0], 2*sigma[0])
        y_lower = x**(variables - 2*sigma)
        y_upper = x**(variables + 2*sigma)

        return(exp_y, y_lower, y_upper, label)

    def expFunc(x, a):
        return x**a

    def ovito_coords(area_name, val):
        scale = get_scale(data_path, area_name)
        return(val/scale)

    ovito = ovito_coords(area, s_dist.val)
    image_folder = image_path + area + '/'
    current_dist = closest_range(image_folder, ovito)
    img = mpimg.imread(get_image(area, ovito_coords(area, s_dist.val)))
    scale = get_scale(data_path, area)
    img_plot.set(title='Clustering distance of: ' + str(int(current_dist * scale)) + ' ft')
    img_plot.imshow(img)
    img_plot.axis('off')

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
