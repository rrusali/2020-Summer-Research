import geopy
import pandas as pd
import os

geolocator = geopy.Nominatim(user_agent='CMU-Student')
data_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,dI))]

count = 1

def get_zipcode(df, geolocator, lat_field, lon_field):
    global count
    location = geolocator.reverse((df[lat_field], df[lon_field]))

    if count < 3:
        count += 1
        print('.'*count)
    else:
        count = 1
        print('.')

    try:
        return location.raw['address']['postcode']
    except:
        pass

def transform_coords(coord_path):
    with open(coord_path) as file:
        coords = pd.read_csv(file, sep=',', names=['x', 'y'])

    # Create the normalized dataframe
    normalized_data = pd.DataFrame()
    measure = [[1, 0], [1, 0]]
    index = 0
    abs_max = 0

    # Find the normalization factor for both x and y
    for letter in ['x', 'y']:
        localMax = coords[letter].max()
        localMin = coords[letter].min()
        abs_local = max(abs(localMax), abs(localMin))

        if abs_local > abs_max:
            abs_max = abs_local

    for letter in ['x', 'y']:
        normalized_data[letter] = coords[letter].divide(abs_max)
        mean = normalized_data[letter].mean()
        normalized_data[letter] = normalized_data[letter].subtract(mean)
        normalized_data[letter] = normalized_data[letter].multiply(10000)

        for scale in range(len(measure[index])):
            num = measure[index][scale]
            num = num/10000
            num = num + mean
            num = num * abs_max
            measure[index][scale] = num

        index += 1

    scale = ((((measure[0][0] - measure[0][1])**2 + (measure[1][0] - measure[1][1])**2)/2)**(1/2))*364000

    # The multiplication factor here comes from the amount of feet in one degree of latitude. It's a rough measure
    line = 'One degree of Ovito coords is about equal to ' + str(int(scale)) + ' feet!'

    # Add in the extra columns and rows necessary in an xyz file
    normalized_data.insert(0, 'test', 'H')
    normalized_data[''] = 0
    normalized_data.loc[-1] = ['', '', '', '']
    normalized_data.index = normalized_data.index + 1
    normalized_data = normalized_data.sort_index()
    r, c = normalized_data.shape

    # Setting one of the 'z' values as 0.01 to prevent degeneracy (lol)
    normalized_data.columns = ['1', '2', '3', '4']
    normalized_data['4'][1] = 0.01
    normalized_data.columns = [r - 1, '', '', '']

    # Found here: https://stackoverflow.com/questions/41428539/data-frame-to-file-txt-python/41428596
    reformatted_path = coord_path[:-4] + '_reformatted.txt'
    normalized_data.to_csv(
        path_or_buf = reformatted_path,
        index=False,
        header=True,
        sep='\t',
        mode='a'
    )

    # Write the scale to a text file
    scale_path = coord_path[:-20] + '_scale.txt'
    with open(scale_path, 'w+') as file:
        file.write(str(line))

    return(reformatted_path, scale)

for name in area_names:
    print('\nNow working on: ' + name)
    open_path = data_path + name + '/' + name + '_building_coords.txt'
    new_dir = 'D:/Research Files/Orientational Order Parameter/Zip Codes/' + name
    os.mkdir(new_dir)

    print('\nCreating dataframe...')
    df = pd.read_csv(open_path, sep=',', names=['Area', 'Longitude', 'Latitude'])
    df = df.drop(['Area'], axis = 1)
    print('Finished!')

    print('\nFinding zip codes...')
    zipcodes = df.apply(
                        get_zipcode,
                        axis=1,
                        geolocator=geolocator,
                        lat_field='Latitude',
                        lon_field='Longitude'
                    )

    zipcodes = zipcodes.to_frame()
    zipcodes.columns = ['ZipCode']
    print('Finished!')

    final_frame = pd.concat([df, zipcodes], axis=1)
    final_frame = final_frame.dropna()

    unique_zips = final_frame.ZipCode.unique()

    for zip in unique_zips:
        print('\nNow extracting zip code: ' + str(zip))
        zip_dir = new_dir + '/' + str(zip)
        os.mkdir(zip_dir)

        temp_frame = final_frame[final_frame['ZipCode'] == zip]
        temp_frame = temp_frame.drop(['ZipCode'], axis=1)

        save_path = zip_dir + '/' + str(zip) + '_building_coords.txt'
        temp_frame.to_csv(save_path, sep=',', index=False, header=False)

        print('Reformatting coords...')
        transform_coords(save_path)
        print('Finished!')
