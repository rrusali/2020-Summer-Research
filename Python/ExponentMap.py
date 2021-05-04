import numpy as np
import geopandas as gpd
import pandas as pd
import os
from scipy.optimize import curve_fit
import math
from statistics import mode
import mapclassify
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt

step = 0.001
final = 0.6

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI)) and dI != 'DistrictofColumbia']

coords_path = 'D:/Research Files/Building Coords/Microsoft'
rows = 99
x = [i for i in range(1, rows+1)]

def plot_data():
    data = get_data()
    join_frame = pd.DataFrame(data).T.reset_index()
    join_frame.columns = ['State', 'MostCommon']

    shp_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/State Borders/states.shp"
    shp_file = gpd.read_file(shp_path)
    shp_file['NAME'] = shp_file['NAME'].str.replace(' ', '')

    for_plotting = shp_file.merge(join_frame, left_on='NAME', right_on='State')
    for_plotting = for_plotting.drop(['STATEFP', 'NAME', 'ALAND', 'AWATER', 'GEOID', 'STATENS', 'AFFGEOID', 'STUSPS', 'LSAD'], axis=1)

    ax = for_plotting.plot(
                            column='MostCommon',
                            cmap='Oranges_r',
                            figsize=(15,9),
                            scheme='Quantiles',
                            k=10,
                            legend=True
                        )

    upper_bounds = mapclassify.Quantiles(for_plotting.MostCommon, k=10).bins

    bounds = []
    for index, upper_bound in enumerate(upper_bounds):
        if index == 0:
            lower_bound = for_plotting.MostCommon.min()
        else:
            lower_bound = upper_bounds[index-1]

        # format the numerical legend here
        bound = f'{lower_bound:.1f} to {upper_bound:.1f}'
        bounds.append(bound)

    # get all the legend labels
    legend_labels = ax.get_legend().get_texts()

    # replace the legend labels
    for bound, legend_label in zip(bounds, legend_labels):
        legend_label.set_text(bound)

    font = font_manager.FontProperties(style='normal', size=12)
    ax.get_legend().set_title('Exponential Law Exponent\n', prop=font)

    ax.set_title('Most Common Exponential Law Exponent for the Continental U.S.', fontsize=20, pad=12)
    ax.set_axis_off()
    ax.get_legend().set_bbox_to_anchor((1.1,0.5))
    plt.setp(ax.get_legend().get_texts(), fontsize='12')
    ax.get_figure()

    save_path = "C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/MostCommonExponents(2).png"
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def get_data():
    data = dict()
    for name in area_names:
        print(name)
        i = 0.01
        exponents = []
        while i <= final:
            coord_path = '%s/%s/%s/%s_%s.txt' % (coords_path, name, name, name, str(i))
            temp_data = pd.read_csv(coord_path, names=['Size'], skiprows=1, nrows=rows)
            temp_data['Size'] = temp_data['Size']/temp_data['Size'].max()
            y = temp_data['Size'].to_list()

            variables, covariance = curve_fit(expFunc, x, y)
            exponents.append(variables[0])

            i += step
            i = round(i, 3)
        first_bin = round_down(min(exponents))
        bins = np.arange(first_bin, 0, 0.1)
        inds = np.digitize(exponents, bins)
        most_common = round(bins[mode(inds)-1], 2)
        print(most_common)
        data[name] = [most_common]
    return(data)

def round_down(n, decimals=1):
    multiplier = 10**decimals
    return(math.floor(n*multiplier)/multiplier)

def expFunc(x, a):
    return x**a

plot_data()
