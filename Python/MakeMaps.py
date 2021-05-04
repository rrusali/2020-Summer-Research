import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import mapclassify
import matplotlib.font_manager as font_manager

name_path = 'D:/Research Files/Building Coords/Microsoft/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI))]

hex_vals = []
for name in area_names:
    print('Now working on: ' + name)
    hex_path = name_path + "%s/%s_2hex_order.txt" % (name, name)

    with open(hex_path) as f:
        hex_vals.append([float(f.read())])

data = dict()
for i in range(len(hex_vals)):
    state = area_names[i]
    hex_val = hex_vals[i]
    data[state] = hex_val

join_frame = pd.DataFrame(data).T.reset_index()
join_frame.columns = ['State', 'HexVal']

shp_path = "C:/Users/novar/Downloads/Research Stuff/GIS Maps/State Borders/states.shp"
shp_file = gpd.read_file(shp_path)
shp_file['NAME'] = shp_file['NAME'].str.replace(' ', '')

for_plotting = shp_file.merge(join_frame, left_on='NAME', right_on='State')
for_plotting = for_plotting.drop(['STATEFP', 'NAME', 'ALAND', 'AWATER', 'GEOID', 'STATENS', 'AFFGEOID', 'STUSPS', 'LSAD'], axis=1)

ax = for_plotting.plot(
                        column='HexVal',
                        cmap='Oranges',
                        figsize=(15,9),
                        scheme='quantiles',
                        k=10,
                        legend=True
                    )

upper_bounds = mapclassify.Quantiles(for_plotting.HexVal, k=10).bins

bounds = []
for index, upper_bound in enumerate(upper_bounds):
    if index == 0:
        lower_bound = for_plotting.HexVal.min()
    else:
        lower_bound = upper_bounds[index-1]

    # format the numerical legend here
    bound = f'{lower_bound:.3f} - {upper_bound:.3f}'
    bounds.append(bound)

# get all the legend labels
legend_labels = ax.get_legend().get_texts()

# replace the legend labels
for bound, legend_label in zip(bounds, legend_labels):
    legend_label.set_text(bound)

font = font_manager.FontProperties(style='normal', size=12)
ax.get_legend().set_title('Two-Fold Orientational Order\n', prop=font)

ax.set_title('Two-Fold Orientational Order for: US States', fontsize=20, pad=12)
ax.set_axis_off()
ax.get_legend().set_bbox_to_anchor((1.1,0.5))
plt.setp(ax.get_legend().get_texts(), fontsize='12')
ax.get_figure()

save_path = "D:/Research Files/Orientational Order Parameter/US_states_hex_map.png"
plt.savefig(save_path, bbox_inches='tight')
plt.close()
