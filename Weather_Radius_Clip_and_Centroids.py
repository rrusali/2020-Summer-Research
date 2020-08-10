### IMPORTANT NOTES: This code requires buffer layers to be already present 
### and selected to work properly.

import processing

layer = iface.activeLayer()

inpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Los Angeles/Building_Footprints-shp/e63e5597-6c0d-464f-8ba1-a7288771575e2020330-1-h41qrd.fsqij.shp'
for feat in layer.getFeatures():
    
    name = str(int(feat['OBJECTID']))
    
    layer.selectByExpression('"OBJECTID"=' + "'" + name + "'")
    
    clippath = QgsProcessingFeatureSourceDefinition('census_tracts_00213b30_7228_4058_a32e_dabc4cb5de75', True)
    outpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Heat Map/Los Angeles/'+ name +'_clip.shp'
    
    processing.run('native:clip', {'INPUT': inpath, 'OVERLAY': clippath, 'OUTPUT': outpath})
    
    newLayer = QgsVectorLayer(outpath, 'temp', 'ogr')
    
    if newLayer.featureCount() > 2:
    
        with open("E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Heat Map/Los Angeles/"+name+'_building_coords.txt', 'w') as file:

            for f in newLayer.getFeatures():

                center = f.geometry().centroid()
                area = f.geometry().area()
                
                x = center.asPoint().x()
                y = center.asPoint().y()

                line = '{},{},{}\n'.format(area, x, y)

                file.write(line)
    