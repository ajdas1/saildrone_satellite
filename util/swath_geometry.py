
import os
import geopandas as gpd
import pandas as pd
import shapely as shp
import xarray as xr

# import file_check
# importlib.reload(file_check)
# from file_check import check_for_product

# import read_product
# importlib.reload(read_product)
# from read_product import read_swath

# import plotting
# importlib.reload(plotting)
# from plotting import plot_swath, set_cartopy_projection, proj


def write_shapefile(data: gpd.GeoDataFrame, filedir: str, filename: str = "shapefile.shp"): 

    data.StartTime = data.StartTime.astype(str)
    data.EndTime = data.EndTime.astype(str)
    # data.to_file(filename)

    if os.path.isdir(filedir):
        fls = os.listdir(filedir)
        _ = [os.remove(f"{filedir}/{fl}" for fl in fls)]
    else:
        os.mkdir(filedir)

    data.to_file(f"{filedir}/{filename}")



def create_swath_polygon_time(data: xr.DataArray) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data).reset_index()
    data_pd = data_pd.drop(["NUMROWS", "NUMCELLS"], axis=1)
    data_pd["buffered_point"] = data_pd[["lon", "lat"]].apply(point_buffer, axis=1)

    # split into individual time stamps
    time_groups = data_pd.groupby(data_pd.time)
    time_subgroups = [time_groups.get_group(x) for x in time_groups.groups]
    
    data_gpd = pd.DataFrame([], columns=["Time", "Points", "Polygon"], index=range(len(time_subgroups)))
    for num, el in enumerate(time_subgroups):
        tmp = []
        tmp.append(el.time.iloc[0])
        tmp.append(shp.MultiPoint(points=el.point.values))
        tmp.append(shp.ops.unary_union(el.buffered_point.values))

        data_gpd.loc[num] = tmp

    return gpd.GeoDataFrame(data_gpd, geometry="Polygon")



def create_swath_polygon(data: xr.DataArray) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data).reset_index()
    data_pd["buffered_point"] = data_pd[["lon", "lat"]].apply(point_buffer, axis=1)
    stime = data_pd.time.iloc[0]
    etime = data_pd.time.iloc[-1]
    data_pd = data_pd[["point", "buffered_point"]]

    vals = [
        stime, etime, 
        shp.ops.unary_union(data_pd.buffered_point.values)
    ]
    data_gpd = pd.DataFrame([], columns=["StartTime", "EndTime", "Polygon"], index=[1])
    data_gpd.iloc[0] = vals


    return gpd.GeoDataFrame(data_gpd, geometry="Polygon")





def create_swath_multipoint(data: xr.DataArray) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data)

    multipoint = shp.MultiPoint(points=data_pd.Point.values)
    gpd_ds = gpd.GeoDataFrame({
        "start_time": data_pd.time.iloc[0], 
        "end_time": data_pd.time.iloc[-1],
        "geometry": [multipoint],
        })
    

    return gpd_ds



def point_buffer(x, resolution: float = 0.5):
    point = shp.Point(x)
    buffer = point.buffer(distance=resolution, cap_style=3)

    return buffer


def convert_data_to_points(data: xr.DataArray) -> pd.DataFrame:

    # converts to a pandas dataframe
    data_pd = data.to_dataframe()

    # assigns a shapely point to each
    
    data_pd["point"] = data_pd[["lon", "lat"]].apply(shp.Point, axis=1)

    return data_pd







# ########### workflow
# product = "ASCAT"

# datadir = "/Users/asavarin/Desktop/work/saildrone_satellite/data"
# savedir = "/Users/asavarin/Desktop/work/saildrone_satellite/figs/test"
# datadir += f"/{product}"
# files = check_for_product(datadir=datadir, format = ".nc")

# # for fl in files:



# fl = files[0]
# data = read_swath(filename=f"{datadir}/{fl}", product=product)




# import geopandas as gpd
# import matplotlib.pyplot as plt









# # buffer = multipoint.buffer(distance=12500)