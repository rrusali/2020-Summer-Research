from ovito.io import import_file
from ovito.io import export_file
from ovito.modifiers import CoordinationAnalysisModifier
import numpy as np

# Specify files and filepaths here
# codes = ['USW00093134', 'USW00023130']
# codes = ['USC00360022', 'USC00360861', 'USC00362574', 'USC00365573', 'USC00365918', 'USW00014762', 'USW00094823']
codes = ['USC00408238']

s1 = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coords Folder/Weather Station Coords/Nashville/'
s3 = '_building_coords_reformatted.txt'

for code in codes:

    file_loc = s1 + code + s3

    save_path = 'E:/Old Downloads Folder/Research Stuff/Jupyter Notebooks/Coordination Analysis Data/Nashville/'

    # This imports the file to Ovito
    pipeline = import_file(file_loc)

    def my_modifier(frame, data):
        data.cell_.is2D = True

    pipeline.modifiers.append(my_modifier)

    modify = CoordinationAnalysisModifier(cutoff = 0.1, number_of_bins = 400)
    pipeline.modifiers.append(modify)

    result = pipeline.compute()

    np.savetxt(save_path + code + '.txt', result.tables['coordination-rdf'].xy())
