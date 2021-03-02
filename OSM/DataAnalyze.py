import os
import pandas as pd
from scipy.optimize import curve_fit
import re
import numpy as np

data_path = 'C:/Users/novar/Downloads/Research Stuff/GIS Maps/Building Coords/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]
step = 0.001
i = float(0.01)
final = 0.150
targets = np.arange(50, 305, 5).tolist()

# Create the dataframe that will hold our clustering results
def createFrame(coords, area_name, i, step, final):
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'

    column_names = ['Ovito Range', 'coeff', 'R2']
    final_frame = pd.DataFrame(columns = column_names)
    s2 = '/' + area_name + '_'

    # The loop that does everything yeet
    while i <= final:

        # I could not figure out how to intelligently round the numbers so make sure to check this before running!!
        i = round(i, 5)
        file_loc = directory + area_name + s2 + str(i) + '.txt'

        with open(file_loc) as file:
            data = pd.read_csv(file, sep = ',', names = ['Size'], skiprows = [0])

        data.index = data.index + 1
        data = data.reset_index()
        xdata = data['index']
        ydata = data['Size']

        with open(file_loc) as f:
            for g, d in enumerate(f):
                pass
        if g > 1:
            variables, covariance = curve_fit(expFunc, xdata, ydata)
            temp_df = pd.DataFrame(
                [[i, variables[0], findR2(expFunc, xdata, ydata, variables)]],
                columns = column_names
            )
            final_frame = final_frame.append(temp_df, ignore_index = True)

        i += step

    return final_frame

# Finding the R^2 value of our curve fitting prediction
# Found here: https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
def findR2(fun, x, y, popt):
    residuals = y - fun(x, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1 - (ss_res/ss_tot)

def expFunc(x, a):
    return 1/(a*x)

# Find the clustering distance that gives us the best R^2 value
def closest_value(df):
    target = 1

    # Code found here: https://stackoverflow.com/questions/30112202/how-do-i-find-the-closest-values-in-a-pandas-series-to-an-input-number
    df_sort = df.iloc[(df['R2']-target).abs().argsort()[:1]]
    return(df_sort['Ovito Range'].item())

# Find the scale
def findScale(data_path, area_name):
    scale = 0
    openpath = data_path + area_name + '/' + area_name + '_scale.txt'

    with open(openpath) as f:
        f = f.read()
        scale = re.sub('[^0-9]', '', f)

    return float(scale)

# Now we create the graph
def store_data(best_range, coords, area_name, scale, df):
    directory = coords.rsplit('/', 1)[0]
    directory = directory + '/'
    s2 = '/' + area_name + '_' + str(best_range) + '.txt'
    file_path = directory + area_name + s2

    # This normalizes the data
    data = pd.read_csv(file_path, sep=',', names=['Size'], skiprows=[0])
    pre_normal_max = data['Size'][0]
    data = data.divide(data['Size'].max())

    points = 40
    new_col = data['Size'][:points]

    new_col.loc[-1] = pre_normal_max
    new_col.index = new_col.index + 1
    new_col = new_col.sort_index()

    # new_col.loc[-1] = int(float(best_range*scale))
    # new_col.index = new_col.index + 1
    # new_col = new_col.sort_index()

    df[area_name] = new_col

for target in targets:
    export_frame = pd.DataFrame()
    print('Range is now: ' + str(target))
    for area_name in area_names:
        print('\nNow working on: ' + area_name)
        reformatted_coords = data_path + area_name + '/' + area_name + '_building_coords_reformatted.txt'

        # print('\nCreating dataframe...')
        # processed_ovito = createFrame(reformatted_coords, area_name, i, step, final)
        # print('Finished!')

        # Find the best R^2 for a -1 exponent
        print('\nSorting the data...')
        scale = findScale(data_path, area_name)
        best_range = round(target/scale, 3)
        print('Finished sorting!')

        # Store the data
        print('\nStoring data...')
        store_data(best_range, reformatted_coords, area_name, scale, export_frame)
        print('Finished!')

    save_dir = 'C:/Users/novar/Downloads/Research Stuff/Jupyter Notebooks/Data Exports/Ranges/'
    file_name = 'OSM_export_all_' + str(target) + '.csv'
    save = save_dir + file_name
    export_frame.to_csv(path_or_buf=save, index=False)
