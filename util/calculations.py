import pandas as pd

from datetime import datetime
from math import radians, sin, cos, acos


def subset_saildrone_time(sd_data: pd.DataFrame, start_time: datetime, end_time: datetime) -> pd.DataFrame:

    return sd_data[(start_time <= sd_data.time) & (sd_data.time <= end_time)].reset_index(drop=True)


def great_circle_distance(x) -> float:

    lon1, lat1, lon2, lat2 = map(radians, [x.sd_lon, x.sd_lat, x.st_lon, x.st_lat])
    r_earth = 6371.
    gc = r_earth * (acos(sin(lat1) * sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1-lon2)))

    return gc