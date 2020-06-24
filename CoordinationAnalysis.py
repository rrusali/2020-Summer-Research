from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import CoordinationAnalysisModifier
import numpy as np

# Specify files and filepaths here

code = 'USW00094823'

s1 = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Weather Station Coords/'
s3 = '_building_coords_reformatted.txt'

file_loc = s1 + code + s3

save_path = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coordination Analysis Data/'

# This imports the file to Ovito

pipeline = import_file(file_loc)

def my_modifier(frame, data):
    data.cell_.is2D = True

pipeline.modifiers.append(my_modifier)

modify = CoordinationAnalysisModifier(cutoff = 0.1, number_of_bins = 400)
pipeline.modifiers.append(modify)

result = pipeline.compute()

np.savetxt(save_path + code + '.txt', result.tables['coordination-rdf'].xy())
