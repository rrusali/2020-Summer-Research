import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import mapclassify

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI))]

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

    ax = for_plotting.plot(
                            column='HexVal',
                            cmap='Reds',
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

    ax.set_title('Two-Fold Orientational Order for: ' + name, fontsize=20, pad=12)
    ax.set_axis_off()
    ax.get_legend().set_bbox_to_anchor((1.4,0.8))
    plt.setp(ax.get_legend().get_texts(), fontsize='12')
    ax.get_figure()

    save_path = "D:/Research Files/Orientational Order Parameter/Counties/%s/%s_hex_map.png" % (name, name)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
