import pandas as pd
import os
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np

step = 0.001
final = 0.6

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI)) and dI != 'DistrictofColumbia']

coords_path = 'D:/Research Files/Building Coords/Microsoft'
rows = 99
x = [i for i in range(1, rows+1)]
sns.set_theme()

def run():
    fig_dims = (10,6)
    for name in area_names:
        save_path = 'C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/Exponent vs. Range/' + name + '_exponent_graph.png'
        fig, ax = plt.subplots(figsize=fig_dims)
        x, y, lower, upper = get_data(name)
        sns.lineplot(x=x, y=y, ax=ax)
        plt.fill_between(x, lower, upper, alpha=0.3)
        plt.xlabel('Distance (ft)',fontsize=18, labelpad=20)
        plt.ylabel('Best Fit Exponent', fontsize=18, labelpad=20)
        plt.title('Best Fit Exponent vs. Range for: ' + name, fontsize=18)
        ax.tick_params(axis='both', which='major', labelsize=14)
        plt.savefig(save_path, bbox_inches='tight', dpi=500)
        plt.close()

def get_data(name):
    print(name)
    i = 0.01
    scale = get_scale(name)
    exponents = []
    distances = []
    lower_bounds = []
    upper_bounds = []
    while i <= final:
        coord_path = '%s/%s/%s/%s_%s.txt' % (coords_path, name, name, name, str(i))
        temp_data = pd.read_csv(coord_path, names=['Size'], skiprows=1, nrows=rows)
        temp_data['Size'] = temp_data['Size']/temp_data['Size'].max()
        y = temp_data['Size'].to_list()

        variables, covariance = curve_fit(expFunc, x, y)
        exponents.append(variables[0])
        sigma = np.sqrt(np.diagonal(covariance))
        lower_bounds.append(float(variables[0] - 2*sigma))
        upper_bounds.append(float(variables[0] + 2*sigma))

        distance = int(i*scale)
        distances.append(distance)

        i += step
        i = round(i, 3)
    return(distances, exponents, lower_bounds, upper_bounds)

def get_scale(area_name, data_path='D:/Research Files/Building Coords/Microsoft/'):
    scale = 0
    openpath = data_path + area_name + '/' + area_name + '_scale.txt'

    with open(openpath) as f:
        f = f.read()
        scale = re.sub('[^0-9]', '', f)

    return float(scale)

def expFunc(x, a):
    return x**a

run()
