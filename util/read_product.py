import geopandas as gpd
import xarray as xr
import yaml
import pandas as pd

from enum import Enum
from file_check import fetch_repo_path, read_config
import os


config = read_config()

class DS(Enum):

    ASCAT = "ASCAT"
    saildrone = "saildrone"



def read_swath(filename: str, product: str) -> xr.DataArray:

    repo_path = fetch_repo_path()


    if product == DS.ASCAT.value:
        data = read_ASCAT(filename=f"{repo_path}/{config['satellite_data_folder']}/{product}/{filename}")
    
    elif product == DS.saildrone.value:
        data = read_saildrone(filename=f"{repo_path}/{config['saildrone_data_folder']}/nc/{filename}")


    # elif product == DS.SARAL:
    #     data = read_SARAL(filename=filename)
    
    return data


def read_ASCAT(filename: str) -> xr.DataArray:

    data = xr.open_dataset(
        filename, 
        engine="netcdf4", 
        mask_and_scale=True, 
        decode_times=True, 
        decode_coords=True, 
        drop_variables=[
            "wvc_index", "model_speed", "model_dir", 
            "ice_prob", "ice_age", "wvc_quality_flag", 
            "bs_distance"
        ])
    

    data = data.set_coords(["time"])
        

    return data



def read_saildrone(filename: str) -> xr.DataArray:


    repo_path = fetch_repo_path()
    data = xr.open_dataset(f"{repo_path}/{config['saildrone_data_folder']}/nc/{filename}", engine="netcdf4", mask_and_scale=True, decode_times=True, decode_coords=True)
    data = data.rename({"latitude": "lat", "longitude": "lon"})
    data = data.set_coords(["lat", "lon"])
    
    return data



def read_shapefile(filedir: str, product: str) -> gpd.GeoDataFrame:

    repo_path = fetch_repo_path()

    if product == "saildrone":
        data = gpd.read_file(f"{repo_path}/{config['saildrone_data_folder']}/shapefile/{filedir}/shapefile.shp")
        data.Time = pd.to_datetime(data.Time)

    else:
        data = gpd.read_file(f"{repo_path}/{config['shapefile_data_folder']}/{product}/{filedir}/shapefile.shp")
        # data.Time = pd.to_datetime(data.Time)
        data.StartTime = pd.to_datetime(data.StartTime)
        data.EndTime = pd.to_datetime(data.EndTime)
    
    return data



def read_in_range_log(config: dict, pass_number: int) -> list:
    repo_path = fetch_repo_path()
    log_path = f"{repo_path}/{config['log_data_folder']}/saildrone_{config['saildrone_number']}_{config['saildrone_year']}_{config['satellite_product']}_swath_in_range_pass{pass_number}.txt"

    try:
        with open(log_path, "r") as fl:
            files = [fl.rstrip() for fl in fl.readlines()]
    except FileNotFoundError:
        files = []
    return files

def read_not_in_range_log(config: dict, pass_number: int) -> list:
    repo_path = fetch_repo_path()
    log_path = f"{repo_path}/{config['log_data_folder']}/saildrone_{config['saildrone_number']}_{config['saildrone_year']}_{config['satellite_product']}_swath_not_in_range_pass{pass_number}.txt"

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



