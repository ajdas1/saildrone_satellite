
import geopandas as gpd
import os
import pandas as pd
import shapely as shp
import xarray as xr

from file_check import fetch_repo_path, read_config


config = read_config()


def write_shapefile(data: gpd.GeoDataFrame, product: str, filename: str):
    """
    write_shapefile(data, product, filename)

    Arguments:
    - data: geopandas dataframe to be written to file
    - product: from which the data comes
    - filename: name of the original data file

    Returns nothing.
    """

    path = fetch_repo_path()

    if product != "saildrone":
        swath_path = (
            f"{path}{os.sep}"
            + f"{config['shapefile_data_folder']}{os.sep}"
            + f"{product}{os.sep}"
            + f"{filename.split('{os.sep}')[-1][:-3]}"
        )
        data.StartTime = data.StartTime.astype(str)
        data.EndTime = data.EndTime.astype(str)

    else:
        swath_path = (
            f"{path}{os.sep}"
            + f"{config['saildrone_data_folder']}{os.sep}"
            + f"shapefile{os.sep}"
            + f"{filename.split('{os.sep}')[-1][:-3]}"
        )
        data.Time = data.Time.astype(str)

    if not os.path.isdir(swath_path):
        os.mkdir(swath_path)

    data.to_file(f"{swath_path}{os.sep}shapefile.shp")


def create_swath_polygon(data: xr.DataArray, product: str) -> gpd.GeoDataFrame:
    """
    data = create_swath_polygon_time(data, product)

    Arguments:
    - data: xarray coordinate data array
    - product: from which the data comes

    Returns:
    - data: a geopandas data frame with polygon geometry for the swath.
    """
    data_pd = convert_data_to_points(data=data, product=product).reset_index()
    data_pd["Buffered_point"] = data_pd[["lon", "lat"]].apply(point_buffer, axis=1)
    stime = data_pd.time.iloc[0]
    etime = data_pd.time.iloc[-1]
    data_pd = data_pd[["Point", "Buffered_point"]]

    vals = [product, stime, etime, shp.ops.unary_union(data_pd.Buffered_point.values)]
    data_gpd = pd.DataFrame(
        [], columns=["Product", "StartTime", "EndTime", "Polygon"], index=[1]
    )
    data_gpd.iloc[0] = vals

    return gpd.GeoDataFrame(data_gpd, geometry="Polygon")


def point_buffer(x, resolution: float = 0.5):
    """
    buffer = point_buffer(x, resolution)

    Arguments:
    - x: the lat and lon of the point location
    - resolution: how far out from the point to extend the buffer

    Returns:
    - buffer: the buffered point - a rectangle aroudn the point
    with the given radius (resolution).
    The resolution should be set in the top-level config file.
    """
    point = shp.Point(x)
    buffer = point.buffer(distance=resolution, cap_style=3)

    return buffer


def convert_data_to_points(data: xr.DataArray, product: str) -> pd.DataFrame:
    """
    data = convert_data_to_points(data, product)

    Arguments:
    - data: xarray of coordinated data
    - product: from which the data comes

    Returns:
    - data: dataframe containing a point for each time given.
    """
    # converts to a pandas dataframe
    data_pd = data.to_dataframe()
    if product == "saildrone":
        data_pd = data_pd.mask(data_pd >= 9e36)

    if data_pd.lon.max() > 180:
        data_pd.lon = (data_pd.lon + 180) % 360 - 180

    # assigns a shapely point to each

    data_pd["Point"] = data_pd[["lon", "lat"]].apply(shp.Point, axis=1)

    return data_pd


def convert_saildrone_coordinates_to_points(data: xr.DataArray) -> gpd.GeoDataFrame:
    """
    data = convert_saildrone_coordinates_to_points(data)

    Arguments:
    - data: xarray of coordinated data

    Returns:
    - data: dataframe containing a point for each time given.
    """
    data_pd = convert_data_to_points(data=data, product="saildrone").reset_index()
    data_pd = data_pd[["time", "Point"]]
    data_pd = data_pd.rename(columns={"time": "Time"})

    data_gpd = gpd.GeoDataFrame(data_pd, geometry="Point")

    return data_gpd


def store_data_as_points(data: xr.DataArray, product: str) -> gpd.GeoDataFrame:
    """
    data = store_data_as_points(data, product)

    Arguments:
    - data: xarray of coordinated data
    - product: from which the data comes

    Returns:
    - data: dataframe containing a point for each time given.
    """
    data_pd = convert_data_to_points(data=data, product=product)
    data_pd = data_pd[["time", "Point"]].reset_index(drop=True)
    data_pd = data_pd.rename(columns={"time": "Time"})
    data_gpd = gpd.GeoDataFrame(data_pd, geometry="Point")

    return data_gpd


def saildrone_intersect(x, saildrone_data) -> bool:
    """
    intersect = saildrone_intersect(x, saildrone_data)

    Arguments:
    - x: satellite swath polygon
    - saildrone_data points

    Returns:
    - intersect: whether the saildrone and swath data intersect.
    """
    sd_data = saildrone_data[
        (x.StartTime <= saildrone_data.Time)
        & (saildrone_data.Time <= x.EndTime)
        & (saildrone_data.geometry != None)
    ]

    return shp.LineString(sd_data.geometry).intersects(x.geometry)





