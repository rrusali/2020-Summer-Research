import pandas as pd
import requests
import re
import base64
import zipfile
import os
import sys
from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import ClusterAnalysisModifier
import numpy as np
from scipy.optimize import curve_fit
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

from qgis.core import (
     QgsApplication,
     QgsProcessingFeedback,
     QgsVectorLayer
)

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Append the path where processing plugin can be found
sys.path.append('/docs/dev/qgis/build/output/python/plugins')

import processing
from processing.core.Processing import Processing
Processing.initialize()

#------------------------------------------------------------------------------

# Specify where you want the files to be saved here!!
footprints_folder = 'D:/Research Files/Building Footprints/Microsoft'
centroids_folder = 'D:/Research Files/Building Coords/Microsoft'

# Get the webpage and put the html into a readable format
url = "https://github.com/Microsoft/USBuildingFootprints"

r = requests.get(url)

# Get the HTML of the site
soup = BeautifulSoup(r.text, 'lxml')
table = soup.find_all('table')[1]

# Find all of the links in the table
links = []
for a in table.find_all('a', href=True):
    links.append(a['href'])

def find_name(link):
    name = link.rsplit('/', 1)[1][:-4]
    return(name)

# Code taken from: https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def download_area_zip(area_name, url):
    save_path = 'area_temp.zip'
    footprints_path = footprints_folder + '/' + str(area_name)

    download_url(url, save_path)

    # Code taken from: https://stackoverflow.com/questions/3451111/unzipping-files-in-python
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(footprints_path)

    os.remove(save_path)

    return(footprints_path)

# # Get the centroids of the buildings from QGIS
# def get_centroids(coords_path, area_name):
#     coords_path = coords_path + '/' + area_name + '.geojson'
#     layer = QgsVectorLayer(coords_path, 'temp', 'ogr')
#     dir_path = os.path.join(centroids_folder, area_name)
#     os.mkdir(dir_path)
#     save_path = dir_path + '/' + area_name + '_building_coords.txt'
#
#     # Save the data
#     with open(save_path, 'w') as file:
#         for f in layer.getFeatures():
#             center = f.geometry().centroid()
#
#             x = center.asPoint().x()
#             y = center.asPoint().y()
#             area = f.geometry().area()
#
#             line = '{},{},{}\n'.format(area, x, y)
#             file.write(line)
#
#     return(save_path)
#
# # Transform the coordinates to an OVITO readable format
# def transform_coords(coord_path):
#     with open(coord_path) as file:
#         coords = pd.read_csv(file, sep=',', names=['Area', 'x', 'y'])
#     coords = coords.drop(['Area'], axis = 1)
#
#     # Create the normalized dataframe
#     normalized_data = pd.DataFrame()
#     measure = [[1, 0], [1, 0]]
#     index = 0
#     abs_max = 0
#
#     # Find the normalization factor for both x and y
#     for letter in ['x', 'y']:
#         localMax = coords[letter].max()
#         localMin = coords[letter].min()
#         abs_local = max(abs(localMax), abs(localMin))
#
#         if abs_local > abs_max:
#             abs_max = abs_local
#
#     for letter in ['x', 'y']:
#         normalized_data[letter] = coords[letter].divide(abs_max)
#         mean = normalized_data[letter].mean()
#         normalized_data[letter] = normalized_data[letter].subtract(mean)
#         normalized_data[letter] = normalized_data[letter].multiply(10000)
#
#         for scale in range(len(measure[index])):
#             num = measure[index][scale]
#             num = num/10000
#             num = num + mean
#             num = num * abs_max
#             measure[index][scale] = num
#
#         index += 1
#
#     scale = ((((measure[0][0] - measure[0][1])**2 + (measure[1][0] - measure[1][1])**2)/2)**(1/2))*364000
#
#     # The multiplication factor here comes from the amount of feet in one degree of latitude. It's a rough measure
#     line = 'One degree of Ovito coords is about equal to ' + str(int(scale)) + ' feet!'
#
#     # Add in the extra columns and rows necessary in an xyz file
#     normalized_data.insert(0, 'test', 'H')
#     normalized_data[''] = 0
#     normalized_data.loc[-1] = ['', '', '', '']
#     normalized_data.index = normalized_data.index + 1
#     normalized_data = normalized_data.sort_index()
#     r, c = normalized_data.shape
#
#     # Setting one of the 'z' values as 0.01 to prevent degeneracy (lol)
#     normalized_data.columns = ['1', '2', '3', '4']
#     normalized_data['4'][1] = 0.01
#     normalized_data.columns = [r - 1, '', '', '']
#
#     # Found here: https://stackoverflow.com/questions/41428539/data-frame-to-file-txt-python/41428596
#     reformatted_path = coord_path[:-4] + '_reformatted.txt'
#     normalized_data.to_csv(
#         path_or_buf = reformatted_path,
#         index=False,
#         header=True,
#         sep='\t',
#         mode='a'
#     )
#
#     # Write the scale to a text file
#     scale_path = coord_path[:-20] + '_scale.txt'
#     with open(scale_path, 'w+') as file:
#         file.write(str(line))
#
#     return(reformatted_path, scale)

# Put the buildings into OVITO and cluster them
def auto_clustering(coords, area_name):
    # Create the directory where we will store the OVITO data
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'
    # os.mkdir(directory + area_name)

    # Define a start and end range as well as step sizes
    step = 0.001
    i = float(0.5) + step
    final = 0.6
    copy_i = i

    # This is the code that interfaces with Ovito
    file_loc = coords
    pipeline = import_file(file_loc)

    while i <= final:
        print('Clustering distance is: ' + str(i))
        pipeline.modifiers.append(ClusterAnalysisModifier(cutoff = i, sort_by_size = True))
        data = pipeline.compute()
        cluster_sizes = np.bincount(data.particles['Cluster'])

        outpath = directory + area_name + '/' + area_name + '_' + str(i) + '.txt'
        np.savetxt(outpath, cluster_sizes[:100])

        i += step

        # This prevents rounding errors
        i = round(i, 5)

    return(copy_i, step, final)

# for link in links[-20:]:
#     name = find_name(link)
#
#     # print('\nNow downloading: ' + name)
#     # footpath = download_area_zip(name, link)
#     # print('Finished downloading!')
#     #
#     # print('\nGetting centroids...')
#     # centroids_path = get_centroids(footpath, name)
#     # print('Finished centroids!')
#     #
#     # print('\nReformatting coordinates...')
#     # reformatted_coords, scale = transform_coords(centroids_path)
#     # print('Finished reformatting!')
#
#     reformatted_coords = "D:/Research Files/Building Coords/Microsoft/" + name + "/" + name + "_building_coords_reformatted.txt"
#
#     print('\nNow clustering ' + name + '...')
#     auto_clustering(reformatted_coords, name)
#     print('Clustering finished!')
