
import os
import geopandas as gpd
import pandas as pd
import shapely as shp
import xarray as xr

from file_check import fetch_repo_path

import yaml


config_file = f"{fetch_repo_path()}/config.yaml"

with open(config_file) as fl:
    config = yaml.load(fl, Loader=yaml.FullLoader)




def check_swath_saildrone_time_match(swath_data: gpd.GeoDataFrame, saildrone_data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    match_data = pd.DataFrame([])
    match_data["time_match"] = (swath_data.StartTime >= saildrone_data.Time.min()) & (swath_data.EndTime <= saildrone_data.Time.max())

    return match_data



def write_shapefile(data: gpd.GeoDataFrame, product: str, filename: str): 
    path = fetch_repo_path()

    if product != "saildrone":
        swath_path = f"{path}/{config['shapefile_data_folder']}/{product}/{filename.split('/')[-1][:-3]}"
        # data.Time = data.Time.astype(str)
        data.StartTime = data.StartTime.astype(str)
        data.EndTime = data.EndTime.astype(str)
        
    else:
        swath_path = f"{path}/{config['saildrone_data_folder']}/shapefile/{filename.split('/')[-1][:-3]}"
        data.Time = data.Time.astype(str)

    if not os.path.isdir(swath_path):
        os.mkdir(swath_path)

    data.to_file(f"{swath_path}/shapefile.shp")



def create_swath_polygon_time(data: xr.DataArray, product: str) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data, product=product).reset_index()
    data_pd = data_pd.drop(["NUMROWS", "NUMCELLS"], axis=1)
    data_pd["Buffered_point"] = data_pd[["lon", "lat"]].apply(point_buffer, resolution=float(config['satellite_dataset_resolution']), axis=1)

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



def create_swath_polygon(data: xr.DataArray, product: str) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data, product=product).reset_index()
    data_pd["Buffered_point"] = data_pd[["lon", "lat"]].apply(point_buffer, axis=1)
    stime = data_pd.time.iloc[0]
    etime = data_pd.time.iloc[-1]
    data_pd = data_pd[["Point", "Buffered_point"]]

    vals = [
        product, stime, etime, 
        shp.ops.unary_union(data_pd.Buffered_point.values)
    ]
    data_gpd = pd.DataFrame([], columns=["Product", "StartTime", "EndTime", "Polygon"], index=[1])
    data_gpd.iloc[0] = vals


    return gpd.GeoDataFrame(data_gpd, geometry="Polygon")





def create_swath_multipoint(data: pd.DataFrame) -> gpd.GeoDataFrame:

    # data_pd = convert_data_to_points(data=data)

    multipoint = shp.MultiPoint(points=data.geometry.values)
    gpd_ds = gpd.GeoDataFrame({
        "StartTime": data.Time.iloc[0], 
        "EndTime": data.Time.iloc[-1],
        "geometry": [multipoint],
        })
    

    return gpd_ds



def point_buffer(x, resolution: float = 0.5):
    point = shp.Point(x)
    buffer = point.buffer(distance=resolution, cap_style=3)

    return buffer


def convert_data_to_points(data: xr.DataArray, product: str) -> pd.DataFrame:
    # converts to a pandas dataframe
    data_pd = data.to_dataframe()
    if product == "saildrone":
        data_pd = data_pd.mask(data_pd >= 9e36)

    if data_pd.lon.max() > 180:
        data_pd.lon = ((data_pd.lon + 180) % 360 - 180)

    # assigns a shapely point to each
    
    data_pd["Point"] = data_pd[["lon", "lat"]].apply(shp.Point, axis=1)

    return data_pd


def convert_saildrone_coordinates_to_points(data: xr.DataArray) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data, product="saildrone").reset_index()
    data_pd = data_pd[["time", "Point"]]
    data_pd = data_pd.rename(columns={"time": "Time"})

    data_gpd = gpd.GeoDataFrame(data_pd, geometry="Point")

    return data_gpd


def store_data_as_points(data: xr.DataArray, product: str) -> gpd.GeoDataFrame:

    data_pd = convert_data_to_points(data=data, product=product)
    data_pd = data_pd[["time", "Point"]].reset_index(drop=True)
    data_pd = data_pd.rename(columns={"time": "Time"})
    data_gpd = gpd.GeoDataFrame(data_pd, geometry="Point")

    return data_gpd


def saildrone_intersect(x, saildrone_data):
    sd_data = saildrone_data[(x.StartTime <= saildrone_data.Time) & (saildrone_data.Time <= x.EndTime) & (saildrone_data.geometry != None)]

    return shp.LineString(sd_data.geometry).intersects(x.geometry)