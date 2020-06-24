from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import ClusterAnalysisModifier
import numpy as np
import os

# Be sure to specify your directories and filepaths here!!

codes = ['USC00360022', 'USC00360861', 'USC00362574', 'USC00365573', 'USC00365918', 'USW00014762', 'USW00094823']

s1 = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Weather Station Coords/'

s2 = '_building_coords_reformatted.txt'

for code in codes:

    # This makes the folder to hold all Coords

    os.mkdir(s1 + code)

    # This is where you set your step size and intended range

    step = 0.001

    i = 0.01

    final = 0.15

    # This is the code that interfaces with Ovito

    file_loc = s1 + code + s2

    pipeline = import_file(file_loc)

    while i <= final:

        pipeline.modifiers.append(ClusterAnalysisModifier(cutoff = i, sort_by_size = True))

        data = pipeline.compute()

        cluster_sizes = np.bincount(data.particles['Cluster'])

        outpath = s1 + code + '/' + code + '_' + str(i) + '.txt'

        np.savetxt(outpath, cluster_sizes)

        i += step

        # I couldn't figure it out so make sure you change the amount of
        # sig figs you need here or else you might just be caught in a loop

        i = round(i, 5)
