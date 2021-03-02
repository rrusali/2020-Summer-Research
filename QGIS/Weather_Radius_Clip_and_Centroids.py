### IMPORTANT NOTES: This code requires buffer layers to be already present 
### and selected to work properly.

import processing

layer = iface.activeLayer()

inpath = 'C:/Users/novar/Downloads/Research Stuff/LA_Building_Footprints-shp/e63e5597-6c0d-464f-8ba1-a7288771575e2020330-1-h41qrd.fsqij.shp'
for feat in layer.getFeatures():
    
    name = str(feat['Station'])
    
    layer.selectByExpression('"Station"=' + "'" + name + "'")
    
    clippath = QgsProcessingFeatureSourceDefinition('Buffered_8b9da284_02ce_4488_91ba_c00fb9408f6d', True)
    outpath = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Clips/Los Angeles/'+ name +'_clip.shp'
    
    processing.run('native:clip', {'INPUT': inpath, 'OVERLAY': clippath, 'OUTPUT': outpath})
    
    newLayer = QgsVectorLayer(outpath, 'temp', 'ogr')
    
    if newLayer.featureCount() > 2:
    
        with open("C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords/Los Angeles/"+name+'_building_coords.txt', 'w') as file:

            for f in newLayer.getFeatures():

                center = f.geometry().centroid()
                area = f.geometry().area()
                
                x = center.asPoint().x()
                y = center.asPoint().y()

                line = '{},{},{}\n'.format(area, x, y)

                file.write(line)
    