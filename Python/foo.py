import os
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from statistics import mode
import matplotlib.pyplot as plt
import imageio
from math import log

coords_path = 'D:/Research Files/Building Coords/Microsoft'
rows = 99
name = 'California'
exponent = -1

def getModeR2(name, exponent):
    i = 0.3
    y_predict = [expFunc(j, exponent) for j in x]
    y_actual = getSizes(name, i)
    y_predict = [log(i) for i in y_predict]
    y_actual = [log(i) for i in y_actual]

    return(y_predict, y_actual)

def getSizes(name, i):
    coord_path = '%s/%s/%s/%s_%s.txt' % (coords_path, name, name, name, str(i))
    temp_data = pd.read_csv(coord_path, names=['Size'], skiprows=1, nrows=rows)
    temp_data['Size'] = temp_data['Size']/temp_data['Size'].max()
    y = temp_data['Size'].to_list()
    return(y)

def expFunc(x, a):
    return x**a

x = [i for i in range(1, 100)]

y_predict, y_actual = getModeR2(name, exponent)

print(r2_score(y_actual, y_predict))

plt.plot(x, y_actual, label='Actual', c='red')
plt.plot(x, y_predict, label='Prediction', c='navy')
plt.legend()
plt.show()
