import pandas as pd
import numpy as np
from datetime import datetime
from math import radians, sin, cos, acos


def get_saildrone_position_extrema(sd_data: pd.DataFrame, buffer: float, lon: str = "lon", lat: str = "lat") -> list:
    extrema = {}
    extrema["lonmin"] = sd_data[lon].min() - buffer
    extrema["lonmax"] = sd_data[lon].max() + buffer
    extrema["latmin"] = sd_data[lat].min() - buffer
    extrema["latmax"] = sd_data[lat].max() + buffer

    return extrema
    



def subset_saildrone_time(sd_data: pd.DataFrame, start_time: datetime, end_time: datetime) -> pd.DataFrame:

    return sd_data[(start_time <= sd_data.time) & (sd_data.time <= end_time)].reset_index(drop=True)


def great_circle_distance(x) -> float:

    lon1, lat1, lon2, lat2 = map(radians, [x.sd_lon, x.sd_lat, x.st_lon, x.st_lat])
    r_earth = 6371.
    gc = r_earth * (acos(sin(lat1) * sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1-lon2)))

    return gc



def match_saildrone_satellite_point(match_data: pd.DataFrame, sd_data: pd.DataFrame, st_data: pd.DataFrame, config: dict):

    sd_var = config["saildrone_variable_name"]
    st_var = config["satellite_variable_name"]
    try:
        sd_data[sd_var].max()
    except AttributeError:
        print(f"     Variable {sd_var} does not exist in saildrone data.")
        print(f"     Existing variables include \n{sd_data.columns}")
    try:
        st_data[st_var].max()
    except AttributeError:
        print(f"     Variable {st_var} does not exist in satellite data.")
        print(f"     Existing variables include \n{st_data.columns}")

    data = pd.DataFrame([], columns=["sd_time", "st_time", "dist", "sd_var", "st_var"], index=range(len(match_data)))
    for idx, row in match_data.iterrows():
        dist = row.dist
        st_idx = (row.st_time, row.st_lat, row.st_lon)
        st_pt = st_data.loc[st_idx]
        sd_idx = (row.sd_time, row.sd_lat, row.sd_lon)
        try:
            sd_pt = sd_data.loc[sd_idx]
            data.iloc[idx] = [row.sd_time, row.st_time, dist, sd_pt[sd_var], st_pt[st_var]]
        except KeyError:
            data.iloc[idx] = [row.sd_time, row.st_time, dist, np.nan, st_pt[st_var]]

    data.sd_time = pd.to_datetime(data.sd_time)
    data.st_time = pd.to_datetime(data.st_time)
    data.dist = data.dist.astype(float)
    data.sd_var = data.sd_var.astype(float)
    data.st_var = data.st_var.astype(float)
    return data
