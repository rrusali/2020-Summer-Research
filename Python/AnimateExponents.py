import os
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from statistics import mode
import matplotlib.pyplot as plt
import imageio
from math import log

step = 0.001
final = 0.6

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI)) and dI != 'DistrictofColumbia']

coords_path = 'D:/Research Files/Building Coords/Microsoft'
rows = 99
x = [i for i in range(1, rows+1)]
exponents = np.arange(-0.1, -3.1, -0.1)

def makeAnimation():
    images = []
    for exponent in exponents:
        exponent = round(exponent, 2)
        save_path = makeMap(exponent)
        images.append(imageio.imread(save_path))
    print('\nMaking gif...')
    gif_path = 'C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/R2 Exponent Maps/R2_animated.gif'
    imageio.mimsave(gif_path, images, duration=0.5)
    print('Done!!')

def makeMap(exponent):
    join_frame = createJoinFrame(exponent)
    shp_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/State Borders/states.shp"
    shp_file = gpd.read_file(shp_path)
    shp_file['NAME'] = shp_file['NAME'].str.replace(' ', '')
    for_plotting = shp_file.merge(join_frame, left_on='NAME', right_on='State')
    for_plotting = for_plotting.drop(['STATEFP', 'NAME', 'ALAND', 'AWATER', 'GEOID', 'STATENS', 'AFFGEOID', 'STUSPS', 'LSAD'], axis=1)

    ax = for_plotting.plot(
                            column='ModeR2',
                            cmap='Reds',
                            legend=True,
                            figsize=(15,9),
                            vmin=0,
                            vmax=1,
                            linewidth=0.8,
                            edgecolor='0.8'
                            )

    ax.axis('off')
    plt.title('Mode R2 for the Log of cluster sizes with an Exponential of: ' + str(exponent), fontsize=18)
    save_path = 'C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/R2 Exponent Maps/' + str(exponent) + '_map.png'
    map = ax.get_figure()
    map.savefig(save_path, bbox_inches='tight', dpi=400)
    plt.close()
    return(save_path)

def createJoinFrame(exponent):
    print('\nExponent is: ' + str(exponent))
    data = dict()
    for name in area_names:
        print(name)
        data[name] = getModeR2(name, exponent)
    frame = pd.DataFrame(data).T.reset_index()
    frame.columns = ['State', 'ModeR2']
    return(frame)

def getModeR2(name, exponent):
    i = 0.01
    r2_values = []
    y_predict = [expFunc(j, exponent) for j in x]
    y_predict = [log(k) for k in y_predict]
    while i < final:
        y_actual = getSizes(name, i)
        y_actual = [log(k) for k in y_actual]
        r2_values.append(round(r2_score(y_actual, y_predict), 2))

        i += step
        i = round(i, 3)
    return([mode(r2_values)])

def getSizes(name, i):
    coord_path = '%s/%s/%s/%s_%s.txt' % (coords_path, name, name, name, str(i))
    temp_data = pd.read_csv(coord_path, names=['Size'], skiprows=1, nrows=rows)
    temp_data['Size'] = temp_data['Size']/temp_data['Size'].max()
    y = temp_data['Size'].to_list()
    return(y)

def expFunc(x, a):
    return x**a

print(getModeR2('California', -1.2))
# makeAnimation()
# print(getModeR2('Alabama', -1))
