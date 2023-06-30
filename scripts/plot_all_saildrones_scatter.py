import pandas as pd
import sys

from calculations import match_saildrone_satellite_point, round_coordinates
from plot import plot_scatterplot_overlap, plot_matching_point_locations
from read_write import (
    read_matching_data_from_file_product,
    get_matching_filenames_across_saildrones,
    get_sd_file_from_match_filename,
    get_sat_file_from_match_filename,
    read_config,
    read_saildrone,
    read_swath,
)


config = read_config()
sd_var = config["saildrone_variable_name"]
st_var = config["satellite_variable_name"]

if not config["plot_all_saildrones_scatter"]:
    sys.exit()

matching_fls = sorted(
    get_matching_filenames_across_saildrones(product=config["satellite_product"])
)


sd_files = [get_sd_file_from_match_filename(fl) for fl in matching_fls]

sd_files_unique = sorted(list(set(sd_files)))
sd_data = {}
for sd in sd_files_unique:
    tmp = round_coordinates(
        data=read_saildrone(filename=sd, masked_nan=True, to_pd=True)
    )
    sd_data[sd] = tmp.set_index(["time", "lat", "lon"])


sat_files = [get_sat_file_from_match_filename(fl) for fl in matching_fls]
sat_files_unique = list(set(sat_files))
sat_data = {}
for sat in sat_files_unique:
    tmp = round_coordinates(data=read_swath(filename=sat, masked_nan=True, as_pd=True))
    sat_data[sat] = tmp.set_index(["time", "lat", "lon"])


match_data = []
for match_fl in matching_fls:
    tmp = round_coordinates(
        data=read_matching_data_from_file_product(filename=match_fl),
        vars=["sd_lon", "sd_lat", "st_lon", "st_lat", "dist"],
    )
    match_data.append(tmp)

combined = []
nearest = []
mean = []
for nmatch in range(len(matching_fls)):
    sd_fl = sd_files[nmatch]
    sat_fl = sat_files[nmatch]
    sd_current = sd_data[sd_fl]
    sat_current = sat_data[sat_fl]
    match_current = match_data[nmatch]

    tmp = match_saildrone_satellite_point(
        match_data=match_current,
        sd_data=sd_current,
        st_data=sat_current,
        sd_var=sd_var,
        st_var=st_var,
    )
    tmp = tmp.dropna(axis=0, thresh=5)
    if len(tmp) > 0:
        combined.append(tmp)
        mean.append(
            tmp.groupby("sd_time", as_index=False).mean().reset_index(drop=True)
        )
        nearest.append(
            tmp.loc[tmp.groupby("sd_time").dist.idxmin()].reset_index(drop=True)
        )

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
    match_data=match_data,
    sd_fls=sd_files,
    matching_fls=matching_fls,
    filename=filename,
    title=title,
)
