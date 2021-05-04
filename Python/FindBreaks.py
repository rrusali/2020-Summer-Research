import pandas as pd
from scipy.optimize import curve_fit
import os
import re
import warnings
import numpy as np

warnings.filterwarnings("ignore")

data_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]

def run():
    for name in area_names[:1]:
        print('Now working on: ' + name)
        i = 0.01
        f = 0.6
        step = 0.001

        export_frame = pd.DataFrame()

        while i <= f:
            cluster_path = data_path + '%s/%s/%s_%s.txt' % (name, name, name, str(i))
            i += step
            i = round(i, 3)

            data = pd.read_csv(cluster_path, names=['Size'], skiprows=1, nrows=100)
            data['Size'] = data['Size']/data['Size'].max()
            points = data['Size'].to_list()

            slopes = get_slopes(points)
            drops = find_drops(slopes, points)

            # if len(drops) > 0:
            scale = get_scale(data_path, name)
            dist = int(scale * i)
            d = {'Distance': dist, 'Drops': [drops]}
            temp_frame = pd.DataFrame(data=d)

            if len(export_frame) > 0:
                prev_drop = export_frame.tail(1)['Drops'].item()
                if temp_frame['Drops'].item() != prev_drop:
                    export_frame = export_frame.append(temp_frame, ignore_index=True)
            else:
                export_frame = export_frame.append(temp_frame, ignore_index=True)

        if len(export_frame) == 0:
            print(name + ' has no drops!')
        save_path = data_path + '%s/%s_drops.csv' % (name, name)
        export_frame.to_csv(save_path, index=False)

def expFunc(x, a):
    return x**a

def get_scale(data_path, area_name):
    scale = 0
    openpath = data_path + area_name + '/' + area_name + '_scale.txt'

    with open(openpath) as f:
        f = f.read()
        scale = re.sub('[^0-9]', '', f)

    return float(scale)

def get_slopes(points):
    slopes = []
    for i in range(len(points)):
        if i > 3:
            x = [i, i-1, i-2, i-3]
            y = [points[i], points[i-1], points[i-2], points[i-3]]
            variables, covariance = curve_fit(expFunc, x, y)
            slopes.append(variables[0])
    return(slopes)

def find_drops(slopes, points):
    drops = []
    for i in range(len(slopes)):
        if i > 3 and len(drops) == 0:
            x = [n for n in range(i) if n > 0]
            y = points[:i-1]
            average_slope, b = curve_fit(expFunc, x, y)
            diff = abs((slopes[i]-average_slope[0])/average_slope[0])
            if diff > 0.4:
                drops.append(i)
        elif i > 3:
            x = [n for n in range(i) if n >= drops[-1]]
            y = points[drops[-1]:i]
            if len(slopes[drops[-1]:i-1]) == 0:
                pass
            else:
                average_slope, b = curve_fit(expFunc, x, y)
                diff = abs((slopes[i]-average_slope[0])/average_slope[0])
                if diff > 0.4:
                    drops.append(i)

    if len(drops) > 0 and drops[0] > 4:
        return drops
    else:
        return(drops[1:])

run()
