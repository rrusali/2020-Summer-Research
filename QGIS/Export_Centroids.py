import os

layer = iface.activeLayer()

directory = 'Utah'
parent_directory = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords/'
dir_path = os.path.join(parent_directory, directory)
os.mkdir(dir_path)

print(dir_path)

save_path = dir_path + '/' + directory + '_building_coords.txt'

with open(save_path, 'w') as file:

    for f in layer.getFeatures():
        
        center = f.geometry().centroid()
        
        x = center.asPoint().x()
        y = center.asPoint().y()
        area = f.geometry().area()

        line = '{},{},{}\n'.format(area, x, y)
        
        file.write(line)
    