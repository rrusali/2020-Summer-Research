import os
import pandas as pd
import sys

from qgis.core import (
     QgsApplication,
     QgsProcessingFeedback,
     QgsVectorLayer,
     QgsProject,
     QgsProcessingFeatureSourceDefinition
)

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Append the path where processing plugin can be found
sys.path.append('/docs/dev/qgis/build/output/python/plugins')

from qgis import processing
from processing.core.Processing import Processing
Processing.initialize()

state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

states = {
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'DistrictofColumbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'NorthCarolina',
        'ND': 'NorthDakota',
        'NE': 'Nebraska',
        'NH': 'NewHampshire',
        'NJ': 'NewJersey',
        'NM': 'NewMexico',
        'NV': 'Nevada',
        'NY': 'NewYork',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'RhodeIsland',
        'SC': 'SouthCarolina',
        'SD': 'SouthDakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'WestVirginia',
        'WY': 'Wyoming'
}

def get_key(val):
    for key, value in state_codes.items():
         if val == value:
             return key

def transform_coords(coord_path):
    with open(coord_path) as file:
        coords = pd.read_csv(file, sep=',', names=['Area', 'x', 'y'], skiprows=1)
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

county_file = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/cb_2019_us_county_20m/cb_2019_us_county_20m.shp"
layer = QgsVectorLayer(county_file, 'counties', 'ogr')

# for alg in QgsApplication.processingRegistry().algorithms():
#         print(alg.id(), "->", alg.displayName())
#
# processing.algorithmHelp("qgis:selectbyexpression")

for feat in layer.getFeatures():
    try:
        statefp = feat['STATEFP']
        state = get_key(str(statefp))
        name = states[state]
        county = feat['COUNTYFP']
        new_dir = 'D:/Research Files/Orientational Order Parameter/Counties/' + name
        county_dir = new_dir + '/' + str(county)

        if len(os.listdir(county_dir)) < 3:
            print('Working on: ' + state + '-' + str(county))

            # file_loc = 'D:/Research Files/Building Coords/Microsoft/%s/%s_building_coords.txt' % (name, name)
            # uri = 'file:///%s?type=csv&useHeader=No&maxFields=10000&detectTypes=yes&xField=field_2&yField=field_3&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no' % (file_loc)
            # buildings = QgsVectorLayer(uri, 'temp', 'delimitedtext')
            #
            # outpath = county_dir + '/' + str(county) + '_building_coords.csv'
            #
            # processing.run("qgis:selectbyexpression", {'INPUT': 'counties', 'EXPRESSION': '"COUNTYFP"='+ "'" + str(county) + "'" + ' AND ' + '"STATEFP"=' + "'" + str(statefp) + "'"})
            # clippath = QgsProcessingFeatureSourceDefinition(layer.id(), True)
            #
            # processing.run("gdal:clipvectorbyextent"    , {'INPUT': 'temp', 'EXTENT': clippath, 'OUTPUT': outpath})
            #
            # new_name = county_dir + '/' + str(county) + '_building_coords.txt'
            # os.rename(outpath, new_name)
            # a,b = transform_coords(new_name)

    except:
        pass
