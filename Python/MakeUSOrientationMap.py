import geopandas as gpd
import os
import mapclassify
import pandas as pd
import matplotlib.pyplot as plt

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI))]

us_frame = gpd.GeoDataFrame()

for name in area_names:

    print('Now working on: ' + name)
    hex_path = "D:/Research Files/Orientational Order Parameter/Counties/%s/%s_2hex_order.csv" % (name, name)
    hex_order = pd.read_csv(hex_path)
    hex_order['County'] = pd.to_numeric(hex_order['County'])

    shp_path = "D:/Research Files/Orientational Order Parameter/Counties/%s/%s_counties.shp" % (name, name)
    shp_file = gpd.read_file(shp_path)
    shp_file['COUNTYFP'] = pd.to_numeric(shp_file['COUNTYFP'])

    for_plotting = shp_file.merge(hex_order, left_on='COUNTYFP', right_on='County')
    for_plotting = for_plotting.drop(['County'], axis=1)

    us_frame = us_frame.append(for_plotting)

ax = us_frame.plot(
                        column='HexVal',
                        cmap='Reds',
                        figsize=(15,9),
                        scheme='quantiles',
                        k=10,
                        legend=True
                    )

ax.set_title('Two-Fold Orientational Order for: ' + 'United States', fontsize=20, pad=12)
ax.set_axis_off()
ax.get_legend().set_bbox_to_anchor((1,0.5))
plt.setp(ax.get_legend().get_texts(), fontsize='12')
ax.get_figure()

save_path = "D:/Research Files/Orientational Order Parameter/Counties/%s_hex_map.png" % ('US')
plt.savefig(save_path)
plt.close()
