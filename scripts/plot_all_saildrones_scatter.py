import pandas as pd
import sys
import importlib
import calculations
importlib.reload(calculations)
from calculations import match_saildrone_satellite_point, round_coordinates
import importlib
import plot
importlib.reload(plot)
from plot import plot_scatterplot_overlap, plot_matching_point_locations
import importlib
import read_write
importlib.reload(read_write)
from read_write import (
    fetch_repo_path,
    read_matching_data_from_file_product,
    get_sd_file_from_match_filename,
    get_sat_file_from_match_filename,
    read_config,
    read_saildrone,
    read_swath,
)
import os

config = read_config()
sd_var = config["saildrone_variable_name"]
st_var = config["satellite_variable_name"]

if not config["plot_all_saildrones_scatter"]:
    sys.exit()

print(
    f"Plotting the scatterplot of all saildrones from "
    + f"to {config['satellite_product']} satellite swaths."
)


sd_dirs = sorted([f"{fetch_repo_path()}/{config['matching_data_folder']}/{fl}" for fl in os.listdir(f"{fetch_repo_path()}/{config['matching_data_folder']}")])

matching_fls = [[f"{sdir}/{config['satellite_product']}/{fl}" for fl in os.listdir(f"{sdir}/{config['satellite_product']}")] for sdir in sd_dirs]

# sd_files = [get_sd_file_from_match_filename(fl) for fl in matching_fls]


combined = []
mean = []
nearest = []
matching_data = {}
sd_files = []
for sd_fls in matching_fls:
    if len(sd_fls) == 0:
        continue
    sd_filename = get_sd_file_from_match_filename(sd_fls[0])
    sd_files.append(sd_filename)
    sd_data = round_coordinates(
        data=read_saildrone(filename=sd_filename, masked_nan=True, to_pd=True)
    )
    sd_data = sd_data.set_index(["time", "lat", "lon"])

    tmp = []
    for fl in sd_fls:
        match_data = round_coordinates(
            data=read_matching_data_from_file_product(filename=fl),
            vars=["sd_lon", "sd_lat", "st_lon", "st_lat", "dist"],
        )
        sat_filename = get_sat_file_from_match_filename(fl)
        sat_data = round_coordinates(data=read_swath(filename=sat_filename, masked_nan=True, as_pd=True))
        sat_data = sat_data.set_index(["time", "lat", "lon"])

        comparison = match_saildrone_satellite_point(
            match_data=match_data,
            sd_data=sd_data,
            st_data=sat_data,
            sd_var=sd_var, 
            st_var=st_var
        )
        comparison = comparison.dropna(thresh=5)

        if len(comparison) == 0:
            continue

        tmp.append(match_data) 
        combined.append(comparison)
        mean.append(
            comparison.groupby("sd_time", as_index=False).mean().reset_index(drop=True)
        )
        nearest.append(
            comparison.loc[comparison.groupby("sd_time").dist.idxmin()].reset_index(drop=True)
        )
    matching_data[sd_filename] = tmp

    
combined = pd.concat(combined)
nearest = pd.concat(nearest)
mean = pd.concat(mean)
combined = combined.sort_values(by=["sd_time", "st_time"]).reset_index(drop=True)
nearest = nearest.sort_values(by=["sd_time", "st_time"]).reset_index(drop=True)
mean = mean.sort_values(by=["sd_time", "st_time"]).reset_index(drop=True)




filename = (
    f"SD_"
    + f"{config['satellite_product']}_scatter_overlap_"
    + f"{config['saildrone_variable_name']}.png"
)
plot_scatterplot_overlap(
    combined_pts=combined,
    mean_pts=mean,
    nearest_pts=nearest,
    filename=filename,
    axmin=0,
    axmax=20,
)

filename = (
    f"SD_"
    + f"{config['satellite_product']}_matching_points_locations_"
    + f"{config['saildrone_variable_name']}.png"
)
title = f"(SD - {config['satellite_product']}) matching point locations"
plot_matching_point_locations(
    match_data=matching_data,
    sd_fls=sd_files,
    filename=filename,
    title=title,
)



