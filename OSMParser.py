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

from qgis.core import (
     QgsApplication,
     QgsProcessingFeedback,
     QgsVectorLayer
)

# Specify where you want the files to be saved here!!
footprints_folder = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Footprints'
centroids_folder = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords'

# Get the webpage and put the html into a readable format
url = "https://wiki.openstreetmap.org/wiki/Microsoft_Building_Footprint_Data"

r = requests.get(url)
df_list = pd.read_html(r.text)
not_california = df_list[2]
not_california = not_california[not_california['State'] != 'California'].reset_index(drop=True)
not_california = not_california[not_california['State'] != 'Other'].reset_index(drop=True)
california = df_list[3]

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Append the path where processing plugin can be found
sys.path.append('/docs/dev/qgis/build/output/python/plugins')

import processing
from processing.core.Processing import Processing
Processing.initialize()

# Prompt user for area
def prompt_user():
    cali_or_not = input('\nSearching in California? [y/n]: ')

    data = california if cali_or_not == 'y' else not_california
    link_index = 3 if cali_or_not == 'y' else 2

    print('\nYour options are:')
    areas = data.iloc[:,0].to_list()
    for area in areas:
        print(area)

    area_name = input('\nChoose your area: ')
    area_row = data[data.iloc[:,0].str.match('^' + str(area_name) + '.*', case=False)]
    area_index = area_row.index[0]
    area_name = area_row.iloc[:,0].to_string(index=False)
    area_link = data.iloc[area_index, link_index]

    print('\nDownloading...')
    footprints_path = download_area_zip(area_name, area_link)
    print('File finished downloading!')

    # Turn the building footprints into centroids
    print('\nGetting centroids...')
    if area_name == 'Bay Area (needs to be further broken apart)':
        area_name = 'Bay_Area'
    if cali_or_not == 'y':
        shp_path = footprints_path + '/' + area_name + '.shp'
    else:
        shp_path = footprints_path + '/bldg_footprints.shp'
    coord_path = get_centroids(shp_path, area_name)
    print('Finished centroids!')

    # Transorm to an OVITO readable format
    print('\nTransforming to OVITO coordinates...')
    (reformatted_coords, scale) = transform_coords(coord_path)
    print('Finished transforming coordinates!')

    # Run the auto clustering code
    print('\nClustering with Ovito...')
    (i, step, final) = auto_clustering(reformatted_coords, area_name)
    print('Finished clustering!')

    # Create the dataframe that holds our OVITO output
    print('\nCreating dataframe...')
    processed_ovito = createFrame(reformatted_coords, area_name, i, step, final)
    print('Finished!')

    # Find the best R^2 for a -1 exponent
    print('\nSorting the data...')
    best_range = closest_value(processed_ovito)
    print('Finished sorting!')

    # Create the data visualization
    print('\nMaking the final graph...')
    fig_path = create_graph(best_range, reformatted_coords, area_name)
    print('Finished! Find the graph at: ' + fig_path)

    # Check if the user wants to download another area
    go_again = input('\nGet another area? [y/n]: ')
    if go_again == 'y':
        prompt_user()
    else:
        print('Thanks for using this tool!\n')

# Code taken from: https://towardsdatascience.com/how-to-get-onedrive-direct-download-link-ecb52a62fee4
def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

# Code taken from: https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def download_area_zip(area_name, url):
    save_path = 'area_temp.zip'
    footprints_path = footprints_folder + '/' + str(area_name)

    down_link = create_onedrive_directdownload(url)
    download_url(down_link, save_path)

    # Code taken from: https://stackoverflow.com/questions/3451111/unzipping-files-in-python
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(footprints_path)

    os.remove(save_path)

    return(footprints_path)

# Get the centroids of the buildings from QGIS
def get_centroids(shp_path, area_name):
    layer = QgsVectorLayer(shp_path, 'temp', 'ogr')
    dir_path = os.path.join(centroids_folder, area_name)
    os.mkdir(dir_path)
    save_path = dir_path + '/' + area_name + '_building_coords.txt'

    # Save the data
    with open(save_path, 'w') as file:
        for f in layer.getFeatures():
            center = f.geometry().centroid()

            x = center.asPoint().x()
            y = center.asPoint().y()
            area = f.geometry().area()

            line = '{},{},{}\n'.format(area, x, y)
            file.write(line)

    return(save_path)

# Transform the coordinates to an OVITO readable format
def transform_coords(coord_path):
    with open(coord_path) as file:
        coords = pd.read_csv(file, sep=',', names=['Area', 'x', 'y'])
    coords = coords.drop(['Area'], axis = 1)

    # Create the normalized dataframe
    normalized_data = pd.DataFrame()
    measure = [[1, 0], [1, 0]]
    index = 0
    abs_max = 0

    # Find the normalization factor for both x and y
    for letter in ['x', 'y']:
        localMax = coords[letter].max()
        localMin = coords[letter].min()
        abs_local = max(abs(localMax), abs(localMin))

        if abs_local > abs_max:
            abs_max = abs_local

    for letter in ['x', 'y']:
        normalized_data[letter] = coords[letter].divide(abs_max)
        mean = normalized_data[letter].mean()
        normalized_data[letter] = normalized_data[letter].subtract(mean)
        normalized_data[letter] = normalized_data[letter].multiply(10000)

        for scale in range(len(measure[index])):
            num = measure[index][scale]
            num = num/10000
            num = num + mean
            num = num * abs_max
            measure[index][scale] = num

        index += 1

    scale = ((((measure[0][0] - measure[0][1])**2 + (measure[1][0] - measure[1][1])**2)/2)**(1/2))*364000

    # The multiplication factor here comes from the amount of feet in one degree of latitude. It's a rough measure
    line = 'One degree of Ovito coords is about equal to ' + str(int(scale)) + ' feet!'

    # Add in the extra columns and rows necessary in an xyz file
    normalized_data.insert(0, 'test', 'H')
    normalized_data[''] = 0
    normalized_data.loc[-1] = ['', '', '', '']
    normalized_data.index = normalized_data.index + 1
    normalized_data = normalized_data.sort_index()
    r, c = normalized_data.shape

    # Setting one of the 'z' values as 0.01 to prevent degeneracy (lol)
    normalized_data.columns = ['1', '2', '3', '4']
    normalized_data['4'][1] = 0.01
    normalized_data.columns = [r - 1, '', '', '']

    # Found here: https://stackoverflow.com/questions/41428539/data-frame-to-file-txt-python/41428596
    reformatted_path = coord_path[:-4] + '_reformatted.txt'
    normalized_data.to_csv(
        path_or_buf = reformatted_path,
        index=False,
        header=True,
        sep='\t',
        mode='a'
    )

    # Write the scale to a text file
    scale_path = coord_path[:-20] + '_scale.txt'
    with open(scale_path, 'w+') as file:
        file.write(str(line))

    return(reformatted_path, scale)

# Put the buildings into OVITO and cluster them
def auto_clustering(coords, area_name):
    # Create the directory where we will store the OVITO data
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'
    os.mkdir(directory + area_name)

    # Define a start and end range as well as step sizes
    step = 0.001
    i = float(0.01)
    final = 0.150
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
        np.savetxt(outpath, cluster_sizes)

        i += step

        # This prevents rounding errors
        i = round(i, 5)

    return(copy_i, step, final)

# Create the dataframe that will hold our clustering results
def createFrame(coords, area_name, i, step, final):
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'

    column_names = ['Ovito Range', 'coeff', 'R2']
    final_frame = pd.DataFrame(columns = column_names)
    s2 = '/' + area_name + '_'

    # The loop that does everything yeet
    while i <= final:

        # I could not figure out how to intelligently round the numbers so make sure to check this before running!!
        i = round(i, 5)
        file_loc = directory + area_name + s2 + str(i) + '.txt'

        with open(file_loc) as file:
            data = pd.read_csv(file, sep = ',', names = ['Size'], skiprows = [0])

        data.index = data.index + 1
        data = data.reset_index()
        xdata = data['index']
        ydata = data['Size']

        with open(file_loc) as f:
            for g, d in enumerate(f):
                pass
        if g > 1:
            variables, covariance = curve_fit(expFunc, xdata, ydata)
            temp_df = pd.DataFrame(
                [[i, variables[0], findR2(expFunc, xdata, ydata, variables)]],
                columns = column_names
            )
            final_frame = final_frame.append(temp_df, ignore_index = True)

        i += step

    return final_frame

# Finding the R^2 value of our curve fitting prediction
# Found here: https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
def findR2(fun, x, y, popt):
    residuals = y - fun(x, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1 - (ss_res/ss_tot)

def expFunc(x, a):
    return 1/(a*x)

# Find the clustering distance that gives us the best R^2 value
def closest_value(df):
    target = 1

    # Code found here: https://stackoverflow.com/questions/30112202/how-do-i-find-the-closest-values-in-a-pandas-series-to-an-input-number
    df_sort = df.iloc[(df['R2']-target).abs().argsort()[:1]]
    return(df_sort['Ovito Range'].item())

# Now we create the graph
def create_graph(best_range, coords, area_name):
    plt.clf()
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'
    s2 = '/' + area_name + '_' + str(best_range) + '.txt'
    file_path = directory + area_name + s2

    # This normalizes the data
    data = pd.read_csv(file_path, sep=',', names=['Size'], skiprows=[0])
    data = data.divide(data['Size'].max())

    points = 40
    zip_graph = sns.scatterplot(y = data['Size'][:points], x = list(range(points)))
    zip_graph.set_title("Zipf's Law Graph for " + area_name)
    zip_graph.set_xlabel('k (ordinal rank by size)')
    zip_graph.set_ylabel('s (normalized size)')

    fig = zip_graph.get_figure()
    savepath = 'C:/Users/novar/Downloads/Research Stuff/Pictures and Figures/' + area_name + '_zip_graph.png'
    fig.savefig(savepath, bbox_inches='tight')

    return(savepath)

prompt_user()
