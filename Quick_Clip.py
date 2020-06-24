import processing

layer = iface.activeLayer()

zip_code = 15228

layer.selectByExpression('ZIP='+str(zip_code))

# This code does the actual clipping
inpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Learning how to find centroids/Allegheny_County_Building_Footprint_Locations.geojson'
clippath = QgsProcessingFeatureSourceDefinition('Allegheny_County_Zip_Code_Boundaries_4006334a_9ab0_41b8_aaea_5bfcb49b313e', True)
outpath = 'E:/Old Downloads Folder/Research Stuff/GIS Maps/Zip Code Stuff/Automated Building Clips/'+str(zip_code)+'_buildings.shp'

processing.run('native:clip', {'INPUT': inpath, 'OVERLAY': clippath, 'OUTPUT': outpath})

# This code iterates through all the features in the layer
#for f in layer.getFeatures():
#    zip_code = f['ZIP']
#    
#    layer.selectByExpression('ZIP='+str(zip_code))