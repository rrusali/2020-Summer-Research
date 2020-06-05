from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import ClusterAnalysisModifier
import numpy as np

zip_code = '15090'

s1 = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/'

s2 = '_building_coords_reformatted.txt'

step = 0.01

i = 0.01

file_loc = s1 + zip_code + s2

pipeline = import_file(file_loc)

while i <= 1:

    pipeline.modifiers.append(ClusterAnalysisModifier(cutoff = i, sort_by_size = True))

    data = pipeline.compute()

    cluster_sizes = np.bincount(data.particles['Cluster'])

    outpath = s1 + zip_code + '/' + zip_code + '_' + str(i) + '.txt'

    np.savetxt(outpath, cluster_sizes)

    i += step

    i = round(i, 2)
