
import xarray as xr

from enum import Enum



class DS(Enum):

    ASCAT = "ASCAT"



def read_swath(filename: str, product: str) -> xr.DataArray:



    if product == "ASCAT":
        data = read_ASCAT(filename=filename)
    
    elif product == "SARAL":
        data = read_SARAL(filename=filename)
    
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


def read_SARAL(filename: str) -> xr.DataArray:
    """
    data = read_SARAL(filename: str, product: str)

    Arguments:
    - filename: name of file to be read in

    Returns:
    - data: DataArray of important variables

    Returned variables: 
    - swh: significant wave height
    - wind_speed_alt: wind speed from altimeter
    - rad_water_vapor: water vapor content (not over land)
    - rad_liquid_water: liquid water content (noto over land)
    - ssha: sea surface height anomaly
    - ssha_dyn: dynamic sea surface height anomaly 
    """


    data = xr.open_dataset(
        filename, 
        engine="netcdf4", 
        mask_and_scale=True, 
        decode_times=True, 
        decode_coords=True, 
        drop_variables=[
            "surface_type", "rad_surf_type",  "ecmwf_meteo_map_avail", 
            "trailing_edge_variation_flag", "ice_flag", "alt", "range",
            "model_dry_tropo_corr", "rad_wet_tropo_corr", "iono_corr_gim",
            "sea_state_bias", "sig0", "mean_topography", "bathymetry", 
            "inv_bar_corr", "hf_fluctuations_corr", "solid_earth_tide",
            "pole_tide", "alt_dyn", "xover_corr"
        ])


    return data



