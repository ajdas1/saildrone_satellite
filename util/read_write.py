import os
import numpy as np
import pandas as pd
import sys
import xarray as xr
import yaml

from enum import Enum


class DS(Enum):
    """
    Enumeration of all the supported datasets.
    """

    ASCAT_METOPB = "ASCAT_METOPB"
    SMAP = "SMAP"
    saildrone = "saildrone"


def fetch_repo_path():
    """
    fetch_repo_path

    Returns:
    - the path to the top-level repository directory.
    """
    path = os.getcwd().split(os.sep)
    try:
        sdp_idx = path.index("saildrone_satellite")
        return os.sep.join(path[: sdp_idx + 1])
    except:
        print("Please run inside repository.")
        sys.exit()


def read_config() -> dict:
    """
    config = read_config()

    Returns:
    - the config dictionary read from the top-level config file.
    """
    config_file = f"{fetch_repo_path()}{os.sep}config.yaml"

    with open(config_file) as fl:
        config = yaml.load(fl, Loader=yaml.FullLoader)

    return config


def create_data_folder_structure(config: dict):
    """
    create_data_folder_structure(config)

    Returns: None
    Creates the directory structure needed for the later steps to run properly.
    It creates the data folders for:
    - satellite data
    - shapefiles of satellite data
    - log files for swath overlap classification with saildrone
    - saildrone data

    The names of the directories can be changed in the top-level config,
    under filename setup.
    If the directories already exist, nothing is done.
    """
    path = fetch_repo_path()

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['satellite_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['satellite_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['log_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['log_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['matching_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['matching_data_folder']}")

    if not os.path.isdir(
        f"{path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['matching_data_folder']}{os.sep}"
            + f"SD{config['saildrone_number']}_{config['saildrone_year']}"
        )

    if not os.path.isdir(
        f"{path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
        + f"{config['satellite_product']}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['matching_data_folder']}{os.sep}"
            + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
            + f"{config['satellite_product']}"
        )

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['figure_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['figure_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['saildrone_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['saildrone_data_folder']}")
        if not os.path.isdir(
            f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"
        ):
            os.mkdir(
                f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"
            )


def register_new_dataset(config: dict):
    """
    register_new_dataset(config)

    Arguments:
    - config - the dictionary from the config yaml file
    Registering a product creates an empty directory for that dataset within
    data_satellite, where you put the downloaded data.
    It also creates a directory for the processed shapefiles belonging to
    that dataset.
    If the directory already exists, nothing is done.
    """
    path = fetch_repo_path()
    product = config["satellite_product"]

    if not os.path.isdir(
        f"{path}{os.sep}" + f"{config['satellite_data_folder']}{os.sep}" + f"{product}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['satellite_data_folder']}{os.sep}"
            + f"{product}"
        )

    if not os.path.isdir(
        f"{path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['matching_data_folder']}{os.sep}"
            + f"SD{config['saildrone_number']}_{config['saildrone_year']}"
        )

    if not os.path.isdir(
        f"{path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
        + f"{product}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['matching_data_folder']}{os.sep}"
            + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
            + f"{product}"
        )


def check_for_saildrone_data(config: dict, sd_number: int = None, sd_year: int = None):
    """
    files = check_for_saildrone_data(config)

    Arguments:
    - config yaml dictionary

    Returns:
    - the filename for the saildrone data.

    Currently, only .nc format is supported, and the file name should
    contain the saildrone year and number.
    """
    path = fetch_repo_path()
    sd_path = f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"

    if sd_number:
        sd_num = sd_number
    else:
        sd_num = config["saildrone_number"]

    if sd_year:
        sd_yr = sd_year
    else:
        sd_yr = config["saildrone_year"]

    files = [
        fl
        for fl in os.listdir(sd_path)
        if str(sd_num) in fl and str(sd_yr) in fl and format in fl
    ]

    if len(files) == 1:
        return files[0]
    elif len(files) == 0:
        print(
            "No saildrone data file. Filename should contain saildrone number and year."
        )
    else:
        print("More than one matching saildrone file.")


def check_for_satellite_data(config: dict, append_datadir: bool = False) -> list[str]:
    """
    files = check_for_product(config)

    Arguments:
    - datadir: directory where data files are located
    - format: what format should be looked for

    Returns:
    - files: list of files in directory with provided format
    """

    path = fetch_repo_path()
    product = config["satellite_product"]
    product_path = (
        f"{path}{os.sep}" + f"{config['satellite_data_folder']}{os.sep}" + f"{product}"
    )

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path) if format in fl])
        if append_datadir:
            files = [f"{product_path}{os.sep}" + f"{fl}" for fl in files]

        return files


def read_in_range_log(config: dict) -> list:
    """
    files = read_in_range_log(config)

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
    files = read_in_range_log(config)


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


def read_saildrone(
    filename: str,
    config: dict,
    masked_nan: bool = False,
    fill_value: float = 9e36,
    to_pd: bool = False,
) -> xr.DataArray:
    """
    data = read_saildrone(filename: str, config, masked_nan: bool, fill_value: float)

    Arguments:
    - filename: name of the file to be read in
    - whether to mask and all-nan rows
    - fill value: value above which things should be masked
    - to_pd: whether to convert to a pandas dataframe

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
    if "WIND_FROM_MEAN" in data.keys():
        data = data.rename({"WIND_FROM_MEAN": "wind_direction"})
    if "WIND_SPEED_MEAN" in data.keys():
        data = data.rename({"WIND_SPEED_MEAN": "wind_speed"})
    if "TEMP_AIR_MEAN" in data.keys():
        data = data.rename({"TEMP_AIR_MEAN": "air_temperature"})
    if "RH_MEAN" in data.keys():
        data = data.rename({"RH_MEAN": "air_relative_humidity"})
    if "BARO_PRES_MEAN" in data.keys():
        data = data.rename({"BARO_PRES_MEAN": "air_pressure"})
    if "TEMP_SBE37_MEAN" in data.keys():
        data = data.rename({"TEMP_SBE37_MEAN": "sea_surface_temperature"})
    if "SAL_SBE37_MEAN" in data.keys():
        data = data.rename({"SAL_SBE37_MEAN": "ocean_salinity"})
    if "WAVE_DOMINANT_PERIOD" in data.keys():
        data = data.rename({"WAVE_DOMINANT_PERIOD": "dominant_wave_period"})
    if "WAVE_SIGNIFICANT_HEIGHT" in data.keys():
        data = data.rename({"WAVE_SIGNIFICANT_HEIGHT": "significant_wave_height"})
    if "WATER_CURRENT_DIRECTION_MEAN" in data.keys():
        data = data.rename({"WATER_CURRENT_DIRECTION_MEAN": "current_direction"})
    if "WATER_CURRENT_SPEED_MEAN" in data.keys():
        data = data.rename({"WATER_CURRENT_SPEED_MEAN": "current_speed"})
    if "trajectory" in data.variables.keys():
        data = data.drop(labels="trajectory")

    if masked_nan:
        masked_data = data.to_dataframe()
        if "time" in masked_data.columns:
            masked_data = masked_data.set_index("time")
        masked_data = masked_data.where(masked_data < fill_value)
        masked_data = masked_data.reset_index()
        masked_data = masked_data[masked_data.lon.notna() & masked_data.lat.notna()]
        masked_data = masked_data.dropna(axis=0, thresh=4)
        if "wind_speed" not in masked_data.columns:
            masked_data["wind_speed"] = np.nan
        if "wind_direction" not in masked_data.columns:
            masked_data["wind_direction"] = np.nan

        if ("2021" in filename) and ("1060" in filename):
            masked_data["wind_speed"].iloc[42000:] = np.nan
            masked_data["wind_direction"].iloc[42000:] = np.nan

        data = masked_data.to_xarray()
        data = data.set_coords(["lat", "lon"])

    if to_pd:
        data = data.to_dataframe().reset_index()

    return data


def write_to_log(filename: str, config: dict, in_range: bool = True):
    """
    write_in_range_to_log(filenames: list, config: dict, in_range: bool)

    Arguments:
    - filenames: list with filenames of swaths
    - in_range: if True, writes to in_range log, if False,
        writes to not_in_range log


    Returns: None

    Writes the filenames of swaths to the associated log file.
    The time window tolerance is specified in the top-level config, in minutes
    (saildrone_time_tolerance_min) - it looks x min ahead and behind the saildrone).
    The maximum allowed distance is specified in the top-level config, in km
    (saildrone_distance_tolerance_km) - it looks within x km of the saildrone
    """
    path = fetch_repo_path()
    if in_range:
        log_path = (
            f"{path}{os.sep}"
            + f"{config['log_data_folder']}{os.sep}"
            + f"saildrone_{config['saildrone_number']}_"
            + f"{config['saildrone_year']}_"
            + f"{config['satellite_product']}_"
            + f"swath_in_range_"
            + f"{config['saildrone_time_tolerance_min']}min_"
            + f"{config['saildrone_distance_tolerance_km']}km"
            + ".txt"
        )
    else:
        log_path = (
            f"{path}{os.sep}"
            + f"{config['log_data_folder']}{os.sep}"
            + f"saildrone_{config['saildrone_number']}_"
            + f"{config['saildrone_year']}_"
            + f"{config['satellite_product']}_"
            + f"swath_not_in_range_"
            + f"{config['saildrone_time_tolerance_min']}min_"
            + f"{config['saildrone_distance_tolerance_km']}km"
            + ".txt"
        )

    with open(log_path, "a") as fl:
        fl.write(filename + "\n")


def write_matching_data_to_file(
    matching_data: pd.DataFrame, matching_file: str, config: dict
):
    repo_path = fetch_repo_path()
    matching_data_path = (
        f"{repo_path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
        + f"{config['satellite_product']}"
    )

    if not os.path.isdir(matching_data_path):
        os.mkdir(matching_data_path)

    current_csv = f"{matching_data_path}{os.sep}{matching_file.split('.')[0]}.csv"
    if not os.path.isfile(current_csv):
        matching_data.to_csv(current_csv, index=False)


def read_matching_data_from_file(config: dict, join_swaths: bool = False):
    repo_path = fetch_repo_path()

    match_path = (
        f"{repo_path}{os.sep}"
        + f"{config['matching_data_folder']}{os.sep}"
        + f"SD{config['saildrone_number']}_{config['saildrone_year']}{os.sep}"
        + f"{config['satellite_product']}"
    )
    match_fls = sorted(os.listdir(match_path))

    match_data = []
    for fl in match_fls:
        data = read_matching_data_from_file_product(filename=f"{match_path}/{fl}")
        match_data.append(data)

    if join_swaths:
        match_data = pd.concat(match_data)

    return match_data


def read_swath(
    filename: str, config: dict, masked_nan: bool = False, as_pd: bool = False
) -> xr.DataArray:
    """
    data = read_swath(filename: str, config: dict)

    Arguments:
    - filename: name of the file to be read in

    Returns:
    - data: an xarray containing data with coordinate awareness.

    If a satellite product is not listed in the DS enumeration,
    you will need to edit this function to provide support, and
    create a read_PRODUCT function below.
    It just needs to rename the latitude and longitude variables
    into lat and lon.
    """
    repo_path = fetch_repo_path()
    product = config["satellite_product"]

    if product == DS.ASCAT_METOPB.value:
        current_filename = (
            f"{repo_path}{os.sep}"
            + f"{config['satellite_data_folder']}{os.sep}"
            + f"{product}{os.sep}"
            + f"{filename}"
        )
        data = read_ASCAT(filename=current_filename, masked_nan=masked_nan)

    if product == DS.SMAP.value:
        current_filename = (
            f"{repo_path}{os.sep}"
            + f"{config['satellite_data_folder']}{os.sep}"
            + f"{product}{os.sep}"
            + f"{filename}"
        )
        data = read_SMAP(filename=current_filename, masked_nan=masked_nan)

    if as_pd:
        data = data.to_dataframe().reset_index()

    return data


def read_ASCAT(filename: str, masked_nan: bool = False) -> xr.DataArray:
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

    if masked_nan:
        data_df = data.to_dataframe().reset_index(drop=True)
        masked_data = data_df[data_df.lon.notna() & data_df.lat.notna()]
        masked_data = masked_data.dropna(axis=0, thresh=4)
        masked_data = masked_data.set_index("time")
        data = masked_data.to_xarray()
        data = data.set_coords(["lat", "lon"])

    return data


def read_SMAP(filename: str, masked_nan: bool = False) -> xr.DataArray:
    """
    data = read_SMAP(filename: str)

    Arguments:
    - filename: name of the file to be read in

    Returns:
    - data: an xarray containing data with coordinate awareness.

    These are the instructions for coordinate renaming for
    SMAP - and what variables to drop.
    """
    data = xr.open_dataset(
        filename,
        engine="netcdf4",
        mask_and_scale=True,
        decode_times=True,
        decode_coords=True,
        drop_variables=[
            "solar_flux",
            "rain",
            "windir",
            "tbdw",
            "tbup",
            "tran",
            "sss_ref",
            "winspd",
            "fice",
            "gice",
            "fland",
            "gland",
        ],
    )

    data = data.set_coords(["time"])
    data.coords["cellon"] = (data.coords["cellon"] + 180) % 360 - 180
    data = data.rename(
        {
            "cellat": "lat",
            "cellon": "lon",
            "surtep": "sst",
            "sss_smap": "salinity_70km",
            "sss_smap_40km": "salinity_40km",
        }
    )
    if masked_nan:
        data_df = data.to_dataframe().reset_index(drop=True)
        masked_data = data_df[data_df.lon.notna() & data_df.lat.notna()]
        masked_data = masked_data.dropna(axis=0, thresh=4)
        masked_data = masked_data.set_index("time")
        data = masked_data.to_xarray()
        data = data.set_coords(["lat", "lon"])

    return data


def get_sd_file_from_match_filename(filename: str, config: dict):
    fn = filename.split(os.sep)
    match_idx = fn.index(config["matching_data_folder"])
    fn = fn[match_idx:]
    sd_str = fn[1]
    sd_number = sd_str.split("_")[0][2:]
    sd_year = sd_str.split("_")[1]

    return check_for_saildrone_data(config=config, sd_number=sd_number, sd_year=sd_year)


def get_sat_file_from_match_filename(filename: str, config: dict):
    fn = filename.split(os.sep)
    match_idx = fn.index(config["matching_data_folder"])
    fn = fn[match_idx:]
    sat_str = fn[-1].split(".")[0]

    sat_fls = check_for_satellite_data(product=config["satellite_product"])
    sat_str = [fl for fl in sat_fls if sat_str in fl][0]

    return sat_str


def read_matching_data_from_file_product(filename: str):
    data = pd.read_csv(filename)
    data.sd_time = pd.to_datetime(data.sd_time, format="%Y-%m-%d %H:%M:%S")
    data.st_time = pd.to_datetime(data.st_time, format="%Y-%m-%d %H:%M:%S")

    return data


def sort_log_file(config: dict, in_range: bool = True):
    path = fetch_repo_path()
    if in_range:
        log_path = (
            f"{path}{os.sep}"
            + f"{config['log_data_folder']}{os.sep}"
            + f"saildrone_{config['saildrone_number']}_"
            + f"{config['saildrone_year']}_"
            + f"{config['satellite_product']}_"
            + f"swath_in_range_"
            + f"{config['saildrone_time_tolerance_min']}min_"
            + f"{config['saildrone_distance_tolerance_km']}km"
            + ".txt"
        )
    else:
        log_path = (
            f"{path}{os.sep}"
            + f"{config['log_data_folder']}{os.sep}"
            + f"saildrone_{config['saildrone_number']}_"
            + f"{config['saildrone_year']}_"
            + f"{config['satellite_product']}_"
            + f"swath_not_in_range_"
            + f"{config['saildrone_time_tolerance_min']}min_"
            + f"{config['saildrone_distance_tolerance_km']}km"
            + ".txt"
        )

    fls = sorted(read_in_range_log())
    with open(log_path, "w") as file:
        for line in fls:
            file.write(line + "\n")

    return log_path
