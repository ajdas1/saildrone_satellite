from read_write import check_for_saildrone_data, read_config, read_in_range_log, read_matching_data_from_file, read_saildrone, read_swath
import pandas as pd

import importlib
import calculations
importlib.reload(calculations)
from calculations import match_saildrone_satellite_point, round_coordinates

import plot
importlib.reload(plot)
from plot import plot_scatterplot_overlap

config = read_config()
sd_var = config["saildrone_variable_name"]
st_var = config["satellite_variable_name"]

if not config["plot_saildrone_satellite_data_scatter"]:
    exit()

satellite_filenames = read_in_range_log()
if len(satellite_filenames) == 0:
    print("     There are no satellite swaths that match the saildrone \nbased on the specified criteria.")
    exit()
saildrone_filename = check_for_saildrone_data(
    sd_number=config["saildrone_number"],
    sd_year=config["saildrone_year"],
    format=".nc",
)    



saildrone_data = read_saildrone(filename=saildrone_filename, masked_nan=True, to_pd=True)
saildrone_data = round_coordinates(data=saildrone_data).set_index(["time", "lat", "lon"])

match_data = read_matching_data_from_file(join_swaths=False)

combined = []
nearest = []
mean = []
for nfl, fl in enumerate(satellite_filenames):
    swath_data = read_swath(filename=fl, masked_nan=True, as_pd=True)
    swath_data = round_coordinates(data=swath_data).set_index(["time", "lat", "lon"])
    swath_match_data = match_data[nfl]
    swath_match_data = round_coordinates(data=swath_match_data, vars=["sd_lon", "sd_lat", "st_lon", "st_lat", "dist"])

    tmp = match_saildrone_satellite_point(match_data=swath_match_data, sd_data=saildrone_data, st_data=swath_data, sd_var=sd_var, st_var=st_var)
    combined.append(tmp)
    nearest.append(tmp[tmp.dist == tmp.dist.min()])
    mean.append(tmp.groupby("sd_time").mean().reset_index())

combined = pd.concat(combined).reset_index(drop=True)
nearest = pd.concat(nearest).reset_index(drop=True)
mean = pd.concat(mean).reset_index(drop=True)


import plot
importlib.reload(plot)
from plot import plot_scatterplot_overlap

filename = f"SD{config['saildrone_number']}." + f"{config['saildrone_year']}_" + f"{config['satellite_product']}_scatter_overlap.png"
plot_scatterplot_overlap(combined_pts=combined, mean_pts=mean, nearest_pts=nearest, filename=filename, axmin=0, axmax=20)