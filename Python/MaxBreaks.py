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

def run():
    breaks = []

    for name in area_names:
        file = "D:/Research Files/Building Coords/Microsoft/%s/%s_drops.csv" % (name, name)
        last_break = findLastBreak(file)
        breaks.append(last_break)

    # bins = np.linspace(math.ceil(min(breaks)), math.floor(max(breaks)), 10) # fixed number of bins
    #
    # plt.xlim([min(breaks)-5, max(breaks)+5])
    #
    # plt.hist(breaks, bins=bins, alpha=0.5)
    # plt.title('Final Breaks')
    # plt.xlabel('Range (ft)')
    # plt.ylabel('Count')
    #
    # plt.show()

    breaks = [[i] for i in breaks]
    data = dict()
    for i in range(len(area_names)):
        state = area_names[i]
        last_break = breaks[i]
        data[state] = last_break
    join_frame = pd.DataFrame(data).T.reset_index()
    join_frame.columns = ['State', 'LastBreak']

    shp_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/State Borders/states.shp"
    shp_file = gpd.read_file(shp_path)
    shp_file['NAME'] = shp_file['NAME'].str.replace(' ', '')

    for_plotting = shp_file.merge(join_frame, left_on='NAME', right_on='State')
    for_plotting = for_plotting.drop(['STATEFP', 'NAME', 'ALAND', 'AWATER', 'GEOID', 'STATENS', 'AFFGEOID', 'STUSPS', 'LSAD'], axis=1)

    ax = for_plotting.plot(
                            column='LastBreak',
                            cmap='Oranges',
                            figsize=(15,9),
                            scheme='quantiles',
                            k=10,
                            legend=True
                        )

    upper_bounds = mapclassify.Quantiles(for_plotting.LastBreak, k=10).bins

    bounds = []
    for index, upper_bound in enumerate(upper_bounds):
        if index == 0:
            lower_bound = for_plotting.LastBreak.min()
        else:
            lower_bound = upper_bounds[index-1]

        # format the numerical legend here
        bound = f'{lower_bound:.0f} - {upper_bound:.0f}'
        bounds.append(bound)

    # get all the legend labels
    legend_labels = ax.get_legend().get_texts()

    # replace the legend labels
    for bound, legend_label in zip(bounds, legend_labels):
        legend_label.set_text(bound)

    font = font_manager.FontProperties(style='normal', size=12)

    ax.get_legend().set_title('Range of Last Break (ft)\n', prop=font)
    ax.set_title('Range of Last Break in Log-Log Slope (ft)', fontsize=20, pad=12)
    ax.set_axis_off()
    ax.get_legend().set_bbox_to_anchor((1.1,0.5))
    plt.setp(ax.get_legend().get_texts(), fontsize='12')
    ax.get_figure()

    save_path = 'C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/FinalBreaks.png'
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def findLastBreak(file):
    with open(file) as f:
        last_line = ''
        for line in f:
            line = line.rstrip()
            line = line.split(',', 1)
            if line[1] != '[]':
                last_line = line[0]

        return(int(last_line))

run()
