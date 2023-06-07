

import importlib
from datetime import datetime
import pandas as pd
import geopandas as gpd

import file_check
importlib.reload(file_check)
from file_check import check_for_product

import read_product
importlib.reload(read_product)
from read_product import read_swath

import plotting
importlib.reload(plotting)
from plotting import plot_swath

import subset
importlib.reload(subset)
from subset import subset_files_in_time_range, subset_swath_time

import swath_geometry
importlib.reload(swath_geometry)
from swath_geometry import write_shapefile, create_swath_polygon, create_swath_polygon_time, create_swath_multipoint


import matplotlib.pyplot as plt
import plotting
importlib.reload(plotting)
from plotting import plot_swath, set_cartopy_projection, proj




########### workflow
product = "ASCAT"

datadir = "/Users/asavarin/Desktop/work/saildrone_satellite/data"
savedir = "/Users/asavarin/Desktop/work/saildrone_satellite/figs/test"
datadir += f"/{product}"

savedir_data = "/Users/asavarin/Desktop/work/saildrone_satellite/data_shapefile"
savedir_data += f"/{product}"






files = check_for_product(datadir=datadir, format = ".nc")




for fl in files:
    print(fl.split('/')[-1][:-3])
    data = read_swath(filename=fl, product=product)
    stime = datetime.now()
    data_gpd = create_swath_polygon(data=data)
    etime = datetime.now()

    write_shapefile(data=data_gpd, filedir=f"{savedir_data}/{fl.split('/')[-1][:-3]}")


# start_time = datetime.strptime("2022-09-25 23:40:00", "%Y-%m-%d %H:%M:%S")
# end_time = datetime.strptime("2022-09-25 23:50:00", "%Y-%m-%d %H:%M:%S")
# data = subset_swath_time(data=data, start_time=start_time, end_time=end_time)


# data_pd = data.to_dataframe()
# def point_buffer(x, resolution: float = 0.5):
#     point = shp.Point(x)
#     buffer = point.buffer(distance=resolution, cap_style=3)

#     return buffer

# data_pd["point"] = data_pd[["lon", "lat"]].apply(point_buffer, axis=1)

# # pgn = shp.ops.unary_union(data_pd.point)

# data_gpd = gpd.GeoDataFrame(data_pd)
# data_gpd = data_gpd.set_geometry("point")
# data_gpd_gb = data_gpd.groupby(data_gpd.time)
# subgroups = [data_gpd_gb.get_group(x) for x in data_gpd_gb.groups]





# sg = 1160
# fig = plt.figure(figsize = (12, 5))
# ax = fig.add_subplot(111, projection=proj)


# subgroups[sg].plot(ax=ax, transform=proj)
# ax.set_title(subgroups[sg].time.iloc[0].strftime("%Y-%m-%d %H:%M:%S"))
# # ax.add_geometries([pgn,], crs=proj, facecolor=".7")
# # polygons.plot(ax=ax, column="tmp")
# set_cartopy_projection(ax=ax)
# plt.savefig("test1.png")
# plt.close("all")









