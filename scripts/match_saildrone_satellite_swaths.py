import os
import pandas as pd
import sys

from calculations import (
    great_circle_distance,
    match_saildrone_satellite_point,
    subset_saildrone_time,
    get_saildrone_position_extrema,
)
from datetime import datetime
from plot import (
    plot_matching_point_locations,
    plot_scatterplot_overlap,
    plot_timeseries_swath_overlap,
)
from read_write import (
    check_for_saildrone_data,
    check_for_satellite_data,
    create_data_folder_structure,
    DS,
    fetch_repo_path,
    get_sd_file_from_match_filename,
    get_sat_file_from_match_filename,
    read_config,
    read_in_range_log,
    read_matching_data_from_file,
    read_matching_data_from_file_product,
    read_not_in_range_log,
    read_saildrone,
    read_swath,
    register_new_dataset,
    write_matching_data_to_file,
    write_to_log,
)


config = read_config()

# create dir structure (in case something is missing)
create_data_folder_structure(config=config)

# register a new dataset (in case not registered yet)
print(f"Working on dataset: {config['satellite_product']}")
register_new_dataset(config=config)
supported_datasets = [e.value for e in DS]
if config["satellite_product"] not in supported_datasets:
    print("     The processing for this dataset has not yet been implemented.")
    print("     You will need to add a processing step before continuing.")
    sys.exit()


if config["match_saildrone_satellite_swaths"]:
    print(
        f"Matching saildrone {config['saildrone_number']} "
        + f"from {config['saildrone_year']} to "
        + f"{config['satellite_product']} satellite swaths."
    )

    saildrone_filename = check_for_saildrone_data(config=config)

    satellite_filenames = check_for_satellite_data(config=config, append_datadir=False)
    fls_in_range = read_in_range_log(config=config)
    fls_not_in_range = read_not_in_range_log(config=config)
    satellite_filenames = [
        fl
        for fl in satellite_filenames
        if (fl not in fls_in_range) and (fl not in fls_not_in_range)
    ]

    if len(satellite_filenames) == 0:
        print("All the satellite swaths have already been compared to this saildrone. ")
    else:
        saildrone_data = read_saildrone(
            filename=saildrone_filename, config=config, masked_nan=True, to_pd=True
        )

        filenames = []
        matching_points = []
        for num, fl in enumerate(satellite_filenames):
            start_time = datetime.now()
            print(f"     {num + 1}/{len(satellite_filenames)}: {fl}", end="")
            swath_data = read_swath(
                filename=fl, config=config, masked_nan=True, as_pd=True
            )
            if len(swath_data) == 0:
                write_to_log(filename=fl, config=config, in_range=False)
                print()
                continue

            saildrone_subset = subset_saildrone_time(
                sd_data=saildrone_data,
                start_time=swath_data.time.iloc[0],
                end_time=swath_data.time.iloc[-1],
            )
            if len(saildrone_subset) == 0:
                write_to_log(filename=fl, config=config, in_range=False)
                print()
                continue

            sd_extrema = get_saildrone_position_extrema(
                sd_data=saildrone_subset,
                buffer=config["saildrone_distance_tolerance_km"] / 10,
            )
            swath_data = swath_data[
                (swath_data.lon >= sd_extrema["lonmin"])
                & (swath_data.lon <= sd_extrema["lonmax"])
                & (swath_data.lat >= sd_extrema["latmin"])
                & (swath_data.lat <= sd_extrema["latmax"])
            ]
            if len(swath_data) == 0:
                write_to_log(filename=fl, config=config, in_range=False)
                print()
                continue

            tmp = swath_data.groupby("time")
            satellite_patches = [
                tmp.get_group(group).reset_index(drop=True) for group in tmp.groups
            ]

            swath_points = []
            for patch in satellite_patches:
                patch_time = patch.time.iloc[0]
                dt = pd.Timedelta(minutes=config["saildrone_time_tolerance_min"])
                saildrone_patch = subset_saildrone_time(
                    sd_data=saildrone_subset,
                    start_time=patch_time - dt,
                    end_time=patch_time + dt,
                )

                if len(saildrone_patch) == 0:
                    continue

                points = pd.DataFrame(
                    [],
                    columns=[
                        "sd_lon",
                        "sd_lat",
                        "sd_time",
                        "st_lon",
                        "st_lat",
                        "st_time",
                    ],
                    index=range(len(saildrone_patch) * len(patch)),
                )

                for sd_point in range(len(saildrone_patch)):
                    lon1 = saildrone_patch.lon.iloc[sd_point]
                    lat1 = saildrone_patch.lat.iloc[sd_point]
                    time1 = saildrone_patch.time.iloc[sd_point]
                    for st_point in range(len(patch)):
                        lon2 = patch.lon.iloc[st_point]
                        lat2 = patch.lat.iloc[st_point]
                        time2 = patch.time.iloc[st_point]

                        points.iloc[sd_point * len(patch) + st_point] = [
                            lon1,
                            lat1,
                            time1,
                            lon2,
                            lat2,
                            time2,
                        ]

                points["dist"] = points.apply(great_circle_distance, axis=1)
                points = points[
                    points.dist <= config["saildrone_distance_tolerance_km"]
                ].reset_index(drop=True)
                if len(points) == 0:
                    continue

                swath_points.append(points)

            end_time = datetime.now()
            dt = (end_time - start_time).total_seconds()

            if len(swath_points) > 0:
                print(f" ({dt:.2f} sec)", end="")
                swath_points = pd.concat(swath_points).reset_index(drop=True)
                print(f"; min distance: {swath_points.dist.min():.2f} km ")
                write_to_log(filename=fl, config=config, in_range=True)
                write_matching_data_to_file(
                    matching_data=swath_points, matching_file=fl, config=config
                )
            else:
                write_to_log(filename=fl, config=config, in_range=False)
                print()

        # _ = sort_log_file(config=config, in_range=True)
        # _ = sort_log_file(config=config, in_range=False)


if config["plot_saildrone_satellite_data_timeseries"]:
    print(
        f"Plotting the swath coverage of {config['saildrone_number']} from "
        + f"{config['saildrone_year']} to "
        + f"{config['satellite_product']} satellite swaths."
    )

    saildrone_filename = check_for_saildrone_data(config=config)

    satellite_filenames = read_in_range_log(config=config)
    if len(satellite_filenames) == 0:
        print(
            "     There are no satellite swaths that match the saildrone \nbased on the specified criteria."
        )
        sys.exit()

    saildrone_data = read_saildrone(
        filename=saildrone_filename, config=config, masked_nan=True, to_pd=True
    )
    match_data = read_matching_data_from_file(config=config, join_swaths=True)

    filename = (
        f"SD{config['saildrone_number']}."
        + f"{config['saildrone_year']}_"
        + f"{config['satellite_product']}_timeseries_overlap_"
        + f"{config['saildrone_variable_name']}.png"
    )
    plot_timeseries_swath_overlap(
        sd_data=saildrone_data, swath_match=match_data, filename=filename, config=config
    )


sd_var = config["saildrone_variable_name"]
st_var = config["satellite_variable_name"]

if config["plot_saildrone_satellite_data_scatter"]:
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
    saildrone_data = saildrone_data.set_index(["time", "lat", "lon"])

    match_data = read_matching_data_from_file(config=config, join_swaths=False)

    combined = []
    nearest = []
    mean = []
    for nfl, fl in enumerate(satellite_filenames):
        swath_data = read_swath(filename=fl, config=config, masked_nan=True, as_pd=True)
        swath_data = swath_data.set_index(["time", "lat", "lon"])
        swath_match_data = match_data[nfl]

        tmp = match_saildrone_satellite_point(
            match_data=swath_match_data,
            sd_data=saildrone_data,
            st_data=swath_data,
            config=config,
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
        )


if config["plot_all_saildrones_scatter"]:
    print(
        f"Plotting the scatterplot of all saildrones from "
        + f"to {config['satellite_product']} satellite swaths."
    )

    sd_dirs = sorted(
        [
            f"{fetch_repo_path()}/{config['matching_data_folder']}/{fl}"
            for fl in os.listdir(
                f"{fetch_repo_path()}/{config['matching_data_folder']}"
            )
        ]
    )

    matching_fls = [
        [
            f"{sdir}/{config['satellite_product']}/{fl}"
            for fl in os.listdir(f"{sdir}/{config['satellite_product']}")
        ]
        for sdir in sd_dirs
    ]

    combined = []
    mean = []
    nearest = []
    matching_data = {}
    sd_files = []
    for sd_fls in matching_fls:
        if len(sd_fls) == 0:
            continue
        sd_filename = get_sd_file_from_match_filename(filename=sd_fls[0], config=config)
        sd_files.append(sd_filename)
        sd_data = read_saildrone(
            filename=sd_filename, config=config, masked_nan=True, to_pd=True
        )
        sd_data = sd_data.set_index(["time", "lat", "lon"])

        tmp = []
        for fl in sd_fls:
            match_data = read_matching_data_from_file_product(filename=fl)
            sat_filename = get_sat_file_from_match_filename(filename=fl, config=config)
            sat_data = read_swath(
                filename=sat_filename, config=config, masked_nan=True, as_pd=True
            )
            sat_data = sat_data.set_index(["time", "lat", "lon"])

            comparison = match_saildrone_satellite_point(
                match_data=match_data,
                sd_data=sd_data,
                st_data=sat_data,
                config=config,
            )
            comparison = comparison.dropna(thresh=5)

            if len(comparison) == 0:
                continue

            tmp.append(match_data)
            combined.append(comparison)
            mean.append(
                comparison.groupby("sd_time", as_index=False)
                .mean()
                .reset_index(drop=True)
            )
            nearest.append(
                comparison.loc[comparison.groupby("sd_time").dist.idxmin()].reset_index(
                    drop=True
                )
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
        config=config,
        filename=filename,
        title=title,
    )
