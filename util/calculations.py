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


def round_coordinates(data: pd.DataFrame, sig_fig: int = 2, vars: list = ["lat", "lon"]) -> pd.DataFrame:
    round_factor = 10**sig_fig
    for var in vars:
        data[var] = np.round(data[var]*round_factor)/round_factor
    
    return data


def match_saildrone_satellite_point(match_data: pd.DataFrame, sd_data: pd.DataFrame, st_data: pd.DataFrame, sd_var: str, st_var: str):

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
