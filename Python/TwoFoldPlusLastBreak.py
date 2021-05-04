import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import geopandas as gpd
import mapclassify
import matplotlib.font_manager as font_manager

data_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]

def plot():
    join_frame = combine_frames()
    shp_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/State Borders/states.shp"
    shp_file = gpd.read_file(shp_path)
    shp_file['NAME'] = shp_file['NAME'].str.replace(' ', '')

    for_plotting = shp_file.merge(join_frame, left_on='NAME', right_on='State')
    for_plotting = for_plotting.drop(['STATEFP', 'NAME', 'ALAND', 'AWATER', 'GEOID', 'STATENS', 'AFFGEOID', 'STUSPS', 'LSAD'], axis=1)

    ax = for_plotting.plot(
                            column='Added',
                            cmap='Blues',
                            figsize=(15,9),
                            scheme='NaturalBreaks',
                            k=10,
                            legend=True
                        )

    upper_bounds = mapclassify.NaturalBreaks(for_plotting.Added, k=10).bins

    bounds = []
    for index, upper_bound in enumerate(upper_bounds):
        if index == 0:
            lower_bound = for_plotting.Added.min()
        else:
            lower_bound = upper_bounds[index-1]

        # format the numerical legend here
        bound = f'{lower_bound:.2f} - {upper_bound:.2f}'
        bounds.append(bound)

    # get all the legend labels
    legend_labels = ax.get_legend().get_texts()

    # replace the legend labels
    for bound, legend_label in zip(bounds, legend_labels):
        legend_label.set_text(bound)

    font = font_manager.FontProperties(style='normal', size=12)
    ax.get_legend().set_title('Distance from 1\n', prop=font)

    ax.set_title('Distance from 1 for normalized 2 fold hex val + noramlized last break distance', fontsize=20, pad=12)
    ax.set_axis_off()
    ax.get_legend().set_bbox_to_anchor((1.1,0.5))
    plt.setp(ax.get_legend().get_texts(), fontsize='12')
    ax.get_figure()

    save_path = "C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/HexValPlusLastBreak.png"
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def combine_frames():
    hex = two_fold()
    breaks = find_breaks()
    combined = hex.merge(breaks, left_on='State', right_on='State')
    combined = combined[combined.State != 'DistrictofColumbia']
    for name in ['HexVal', 'LastBreak']:
        combined[name] = (combined[name]-combined[name].min())/(combined[name].max()-combined[name].min())
    combined['Added'] = combined['HexVal'] + combined['LastBreak']
    combined['Added'] = abs(combined['Added']-1)
    return(combined)

def two_fold():
    hex_vals = []
    for name in area_names:
        hex_path = data_path + "%s/%s_2hex_order.txt" % (name, name)

        with open(hex_path) as f:
            hex_vals.append([float(f.read())])

    data = dict()
    for i in range(len(hex_vals)):
        state = area_names[i]
        hex_val = hex_vals[i]
        data[state] = hex_val

    join_frame = pd.DataFrame(data).T.reset_index()
    join_frame.columns = ['State', 'HexVal']
    return(join_frame)

def find_breaks():
    breaks = []

    for name in area_names:
        file = "D:/Research Files/Building Coords/Microsoft/%s/%s_drops.csv" % (name, name)
        last_break = findLastBreak(file)
        breaks.append(last_break)

    breaks = [[i] for i in breaks]
    data = dict()
    for i in range(len(area_names)):
        state = area_names[i]
        last_break = breaks[i]
        data[state] = last_break
    join_frame = pd.DataFrame(data).T.reset_index()
    join_frame.columns = ['State', 'LastBreak']
    return(join_frame)

def findLastBreak(file):
    with open(file) as f:
        last_line = ''
        for line in f:
            line = line.rstrip()
            line = line.split(',', 1)
            if line[1] != '[]':
                last_line = line[0]

        return(int(last_line))

plot()
