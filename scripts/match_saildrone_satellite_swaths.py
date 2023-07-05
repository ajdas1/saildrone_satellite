import pandas as pd
import sys

from calculations import great_circle_distance, subset_saildrone_time
from datetime import datetime
from read_write import (
    check_for_saildrone_data,
    check_for_satellite_data,
    read_config,
    read_in_range_log,
    read_not_in_range_log,
    read_saildrone,
    read_swath,
    write_matching_data_to_file,
    write_to_log,
)


config = read_config()

if not config["match_saildrone_satellite_swaths"]:
    sys.exit()


print(
    f"Matching saildrone {config['saildrone_number']} "
    + f"from {config['saildrone_year']} to "
    + f"{config['satellite_product']} satellite swaths."
)

saildrone_filename = check_for_saildrone_data(
    sd_number=config["saildrone_number"],
    sd_year=config["saildrone_year"],
    format=".nc",
)

satellite_filenames = check_for_satellite_data(
    product=config["satellite_product"], append_datadir=False
)
fls_in_range = read_in_range_log()
fls_not_in_range = read_not_in_range_log()
satellite_filenames = [
    fl
    for fl in satellite_filenames
    if (fl not in fls_in_range) and (fl not in fls_not_in_range)
]

if len(satellite_filenames) == 0:
    print("All the satellite swaths have already been compared to this saildrone. ")
    exit()


saildrone_data = read_saildrone(
    filename=saildrone_filename, masked_nan=True, to_pd=True
)


filenames = []
matching_points = []
for num, fl in enumerate(satellite_filenames):
    start_time = datetime.now()
    print(f"     {num + 1}/{len(satellite_filenames)}: {fl}", end="")
    import importlib
    import read_write
    importlib.reload(read_write)
    from read_write import read_swath
    swath_data = read_swath(filename=fl, masked_nan=True, as_pd=True)

    saildrone_subset = subset_saildrone_time(
        sd_data=saildrone_data,
        start_time=swath_data.time.iloc[0],
        end_time=swath_data.time.iloc[-1],
    )

    sd_patch_swath = []
    st_patch_swath = []
    dist_patch_swath = []

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

        if len(saildrone_patch) > 0:
            points = pd.DataFrame(
                [],
                columns=["sd_lon", "sd_lat", "sd_time", "st_lon", "st_lat", "st_time"],
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
            if len(points) > 0:
                swath_points.append(points)

    end_time = datetime.now()
    dt = (end_time - start_time).total_seconds()
    print(f" ({dt:.2f} sec)", end="")

    if len(swath_points) > 0:
        swath_points = pd.concat(swath_points).reset_index(drop=True)
        print(f"; min distance: {swath_points.dist.min():.2f} km ")
        write_to_log(filename=fl, in_range=True)
        write_matching_data_to_file(matching_data=swath_points, matching_file=fl)
    else:
        write_to_log(filename=fl, in_range=False)
        print()
