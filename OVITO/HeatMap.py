from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import ClusterAnalysisModifier
import numpy as np
import os

dist = 0.05

s1 = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Heat Map/Pittsburgh/'
s2 = '_building_coords_reformatted.txt'

save1 = s1 + '0.05/'

for i in range(1, 403):
    savepath = save1 + str(i) + '.txt'
    openpath = s1 + str(i) + s2

    pipeline = import_file(openpath)
    pipeline.modifiers.append(ClusterAnalysisModifier(cutoff = dist, sort_by_size = True))
    data = pipeline.compute()
    cluster_sizes = np.bincount(data.particles['Cluster'])
    np.savetxt(savepath, cluster_sizes)
