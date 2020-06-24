### IMPORTANT NOTES: This code requires buffer layers to be already present 
### and selected to work properly.

import processing

layer = iface.activeLayer()

inpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Learning how to find centroids/Allegheny_County_Building_Footprint_Locations.geojson'

for feat in layer.getFeatures():
    
    name = feat['Station']
    
    layer.selectByExpression('"Station"=' + "'" + name + "'")
    
    clippath = QgsProcessingFeatureSourceDefinition('weather_clips_d75f6e40_b3a0_48a7_b83c_fdf5ef4cdc93', True)
    outpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Weather Station Clips/'+ name +'_clip.shp'
    
    processing.run('native:clip', {'INPUT': inpath, 'OVERLAY': clippath, 'OUTPUT': outpath})
    
    newLayer = QgsVectorLayer(outpath, 'temp', 'ogr')
    
    with open("E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Weather Station Coords/"+name+'_building_coords.txt', 'w') as file:

        for f in newLayer.getFeatures():

            center = f.geometry().centroid()
            type = f['CLASS']
            area = f.geometry().area()
            
            x = center.asPoint().x()
            y = center.asPoint().y()

            line = '{},{},{},{}\n'.format(type, area, x, y)

            file.write(line)
    