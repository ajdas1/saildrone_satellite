import pandas as pd
import sys

from calculations import match_saildrone_satellite_point, round_coordinates
from plot import plot_scatterplot_overlap
from read_write import (
    check_for_saildrone_data,
    read_config,
    read_in_range_log,
    read_matching_data_from_file,
    read_saildrone,
    read_swath,
)


config = read_config()
sd_var = config["saildrone_variable_name"]
st_var = config["satellite_variable_name"]

if not config["plot_saildrone_satellite_data_scatter"]:
    sys.exit()

print(
    f"Plotting the scatterplot of {config['saildrone_number']} from "
    + f"{config['saildrone_year']} to "
    + f"{config['satellite_product']} satellite swaths."
)

satellite_filenames = read_in_range_log(config=config)
if len(satellite_filenames) == 0:
    print(
        "     There are no satellite swaths that match the saildrone \nbased on the specified criteria."
    )
    exit()
saildrone_filename = check_for_saildrone_data(config=config)


saildrone_data = read_saildrone(
    filename=saildrone_filename, config=config, masked_nan=True, to_pd=True
)
saildrone_data = round_coordinates(data=saildrone_data).set_index(
    ["time", "lat", "lon"]
)

match_data = read_matching_data_from_file(join_swaths=False)

combined = []
nearest = []
mean = []
for nfl, fl in enumerate(satellite_filenames):
    swath_data = read_swath(filename=fl, masked_nan=True, as_pd=True)
    swath_data = round_coordinates(data=swath_data).set_index(["time", "lat", "lon"])
    swath_match_data = match_data[nfl]
    swath_match_data = round_coordinates(
        data=swath_match_data, vars=["sd_lon", "sd_lat", "st_lon", "st_lat", "dist"]
    )

    tmp = match_saildrone_satellite_point(
        match_data=swath_match_data,
        sd_data=saildrone_data,
        st_data=swath_data,
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

if len(combined) > 0:
    combined = pd.concat(combined).reset_index(drop=True)
    nearest = pd.concat(nearest).reset_index(drop=True)
    mean = pd.concat(mean).reset_index(drop=True)

    filename = (
        f"SD{config['saildrone_number']}."
        + f"{config['saildrone_year']}_"
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
