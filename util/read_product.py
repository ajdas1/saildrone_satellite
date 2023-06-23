import geopandas as gpd
import os
import pandas as pd
import xarray as xr

from enum import Enum
from file_check import fetch_repo_path, read_config


config = read_config()


class DS(Enum):
    """
    Enumeration of all the supported datasets.
    """

    ASCAT = "ASCAT"
    saildrone = "saildrone"


def read_swath(filename: str, product: str) -> xr.DataArray:
    """
    data = read_swath(filename: str, product: str)

    Arguments:
    - filename: name of the file to be read in
    - product: the satellite product to be read in.

    Returns:
    - data: an xarray containing data with coordinate awareness.

    If a satellite product is not listed in the DS enumeration,
    you will need to edit this function to provide support, and
    create a read_PRODUCT function below.
    It just needs to rename the latitude and longitude variables
    into lat and lon.
    """
    repo_path = fetch_repo_path()

    if product == DS.ASCAT.value:
        data = read_ASCAT(
            filename=f"{repo_path}{os.sep}"
            + f"{config['satellite_data_folder']}{os.sep}"
            + f"{product}{os.sep}"
            + f"{filename}"
        )

    elif product == DS.saildrone.value:
        data = read_saildrone(
            filename=f"{repo_path}{os.sep}"
            + f"{config['saildrone_data_folder']}{os.sep}"
            + f"nc{os.sep}"
            + f"{filename}"
        )

    # elif product == DS.SARAL:
    #     data = read_SARAL(filename=filename)

    return data


def read_ASCAT(filename: str) -> xr.DataArray:
    """
    data = read_ASCAT(filename: str)

    Arguments:
    - filename: name of the file to be read in

    Returns:
    - data: an xarray containing data with coordinate awareness.

    These are the instructions for coordinate renaming for
    ASCAT - and what variables to drop.
    """
    data = xr.open_dataset(
        filename,
        engine="netcdf4",
        mask_and_scale=True,
        decode_times=True,
        decode_coords=True,
        drop_variables=[
            "wvc_index",
            "model_speed",
            "model_dir",
            "ice_prob",
            "ice_age",
            "wvc_quality_flag",
            "bs_distance",
        ],
    )

    data = data.set_coords(["time"])
    data.coords['lon'] = (data.coords['lon'] + 180) % 360 - 180

    return data


def read_saildrone(filename: str, masked_nan: bool = False, fill_value: float = 9e36) -> xr.DataArray:
    """
    data = read_saildrone(filename: str)

    Arguments:
    - filename: name of the file to be read in

    Returns:
    - data: an xarray containing data with coordinate awareness.

    These are the instructions for coordinate renaming for
    saildrone netcdf files - and what variables to drop.
    """
    repo_path = fetch_repo_path()
    data = xr.open_dataset(
        f"{repo_path}{os.sep}"
        + f"{config['saildrone_data_folder']}{os.sep}"
        + f"nc{os.sep}"
        + f"{filename}",
        engine="netcdf4",
        mask_and_scale=True,
        decode_times=True,
        decode_coords=True,
    )



    data = data.rename({"latitude": "lat", "longitude": "lon"})

    if masked_nan:
        fill_value = 9e36
        masked_data = data.to_dataframe()
        masked_data = masked_data.where(masked_data < fill_value)
        masked_data = masked_data[masked_data.lon.notna() & masked_data.lat.notna()]
        masked_data = masked_data.dropna(axis=0, thresh=3)
        data = masked_data.to_xarray()

    # if masked_nan:
    #     masked_data = data.where(data < fill_value)
    #     masked_data = masked_data.where(masked_data.lon < fill_value)
    #     masked_data = masked_data.where(masked_data.lat < fill_value)
    #     data = masked_data

    data = data.set_coords(["lat", "lon"])
    return data


def read_shapefile(filedir: str, product: str) -> gpd.GeoDataFrame:
    """
    data = read_shapefile(filename: str, product: str)

    Arguments:
    - filename: name of the file to be read in
    - product: name of the product to be read in

    Returns:
    - data: a geodataframe including shapefile information.

    Reads in the data and converts dates into datetime.
    """

    repo_path = fetch_repo_path()

    if product == "saildrone":
        data = gpd.read_file(
            f"{repo_path}{os.sep}"
            + f"{config['saildrone_data_folder']}{os.sep}"
            + f"shapefile{os.sep}"
            + f"{filedir}{os.sep}"
            + f"shapefile.shp"
        )
        data.Time = pd.to_datetime(data.Time)

    else:
        data = gpd.read_file(
            f"{repo_path}{os.sep}"
            + f"{config['shapefile_data_folder']}{os.sep}"
            + f"{product}{os.sep}"
            + f"{filedir}{os.sep}"
            + f"shapefile.shp"
        )
        data.StartTime = pd.to_datetime(data.StartTime)
        data.EndTime = pd.to_datetime(data.EndTime)

    return data


def read_in_range_log(config: dict) -> list:
    """
    files = read_in_range_log(config: dict, pass_number: int)

    Arguments:
    - config: top-level config dictionary
    - pass_number: which range log to look at

    Returns:
    - files: a list of files within that log
    """

    repo_path = fetch_repo_path()
    log_path = (
        f"{repo_path}{os.sep}"
        + f"{config['log_data_folder']}{os.sep}"
        + f"saildrone_{config['saildrone_number']}_"
        + f"{config['saildrone_year']}_"
        + f"{config['satellite_product']}_swath_in_range_"
        + f"{config['saildrone_time_tolerance_min']}min_"
        + f"{config['saildrone_distance_tolerance_km']}km"
        + ".txt"
    )

    try:
        with open(log_path, "r") as fl:
            files = [fl.rstrip() for fl in fl.readlines()]
    except FileNotFoundError:
        files = []
    return files


def read_not_in_range_log(config: dict) -> list:
    """
    files = read_in_range_log(config: dict, pass_number: int)

    Arguments:
    - config: top-level config dictionary
    - pass_number: which range log to look at

    Returns:
    - files: a list of files within that log
    """
    repo_path = fetch_repo_path()
    log_path = (
        f"{repo_path}{os.sep}"
        + f"{config['log_data_folder']}{os.sep}"
        + f"saildrone_{config['saildrone_number']}_"
        + f"{config['saildrone_year']}_"
        + f"{config['satellite_product']}_swath_not_in_range_"
        + f"{config['saildrone_time_tolerance_min']}min_"
        + f"{config['saildrone_distance_tolerance_km']}km"
        + ".txt"
    )

    try:
        with open(log_path, "r") as fl:
            files = [fl.rstrip() for fl in fl.readlines()]
    except FileNotFoundError:
        files = []
    return files


# def read_SARAL(filename: str) -> xr.DataArray:
#     """
#     data = read_SARAL(filename: str, product: str)

#     Arguments:
#     - filename: name of file to be read in

#     Returns:
#     - data: DataArray of important variables

#     Returned variables:
#     - swh: significant wave height
#     - wind_speed_alt: wind speed from altimeter
#     - rad_water_vapor: water vapor content (not over land)
#     - rad_liquid_water: liquid water content (noto over land)
#     - ssha: sea surface height anomaly
#     - ssha_dyn: dynamic sea surface height anomaly
#     """


#     data = xr.open_dataset(
#         filename,
#         engine="netcdf4",
#         mask_and_scale=True,
#         decode_times=True,
#         decode_coords=True,
#         drop_variables=[
#             "surface_type", "rad_surf_type",  "ecmwf_meteo_map_avail",
#             "trailing_edge_variation_flag", "ice_flag", "alt", "range",
#             "model_dry_tropo_corr", "rad_wet_tropo_corr", "iono_corr_gim",
#             "sea_state_bias", "sig0", "mean_topography", "bathymetry",
#             "inv_bar_corr", "hf_fluctuations_corr", "solid_earth_tide",
#             "pole_tide", "alt_dyn", "xover_corr"
#         ])


#     return data
