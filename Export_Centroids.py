layer = QgsVectorLayer("E:/Old Downloads Folder/Research Stuff/GIS Maps/Zip Code Stuff/Automated Building Clips/15108_buildings.shp",\
'temp', 'ogr')

with open("E:/Old Downloads Folder/Research Stuff/GIS Maps/Test Maps/Learning PyQGIS/test1.txt", 'w')\
as file:

    for f in layer.getFeatures():
        
        center = f.geometry().centroid()
        
        x = center.asPoint().x()
        y = center.asPoint().y()

        line = '{},{}\n'.format(x, y)
        
        file.write(line)
    