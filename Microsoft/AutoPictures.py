from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import ClusterAnalysisModifier
from ovito.vis import Viewport
from ovito.data import *
import os

coords_path = 'D:/Research Files/Building Coords/Microsoft/'
save_path = "D:/Research Files/Clustering Images/"

data_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]

final = 0.6
step = 0.025
vp = Viewport()

def setup_particle_types(frame, data):
    types = data.particles_.particle_types_
    types.type_by_id_(1).radius = 0.3

for name in area_names:

    print('Now working on: ' + name)

    i = 0.05
    # os.mkdir(save_path + name)
    datapath = coords_path + name + '/' + name + '_building_coords_reformatted.txt'
    pipeline = import_file(datapath)
    pipeline.add_to_scene()
    pipeline.modifiers.append(setup_particle_types)

    while i <= final:
        print('Distance is: ' + str(i))
        pipeline.modifiers.append(ClusterAnalysisModifier(cutoff = i, sort_by_size = True, cluster_coloring=True))

        vp.zoom_all()
        vp.render_image(filename=save_path + name + '/' + str(i) + '.png', size=(1000,1000), crop=True)
        i += step
        i = round(i, 3)
    pipeline.remove_from_scene()
