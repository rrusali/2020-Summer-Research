import sys
import os

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

# Establish the data source and input into QGIS
footprints_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Footprints/Utah/bldg_footprints.shp"
layer = QgsVectorLayer(footprints_path, 'Utah', 'ogr')

# Create the directory we're saving the footprint data in
directory = 'Utah'
parent_directory = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords'
dir_path = os.path.join(parent_directory, directory)
os.mkdir(dir_path)

save_path = dir_path + '/' + directory + '_building_coords.txt'

# Save the data
with open(save_path, 'w') as file:

    for f in layer.getFeatures():

        center = f.geometry().centroid()

        x = center.asPoint().x()
        y = center.asPoint().y()
        area = f.geometry().area()

        line = '{},{},{}\n'.format(area, x, y)

        file.write(line)
