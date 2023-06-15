import pandas as pd
from file_check import (
    read_config,
    check_for_saildrone_shapefile,
    write_range_not_range_to_log,
)
from read_product import read_shapefile, read_in_range_log, read_swath
from shapefile_geometry import store_data_as_points

config = read_config()


if not config["match_saildrone_satellite_swaths_pass2"]:
    print("Skipping matching saildrone data to satellite swaths - pass 2.")
else:
    print(
        f"Second pass matching saildrone {config['saildrone_number']} from "
        + f"{config['saildrone_year']} to  "
        + f"{config['satellite_product']} satellite swaths."
    )

    saildrone_shp_dir = check_for_saildrone_shapefile(
        sd_number=config["saildrone_number"], sd_year=config["saildrone_year"]
    )
    satellite_shp_fls_1 = read_in_range_log(config=config, pass_number=1)
    satellite_shp_fls_2 = read_in_range_log(config=config, pass_number=2)

    satellite_shp_fls = [
        fl for fl in satellite_shp_fls_1 if fl not in satellite_shp_fls_2
    ]

    if len(satellite_shp_fls) == 0:
        print("All the satellite swaths have already been compared to this saildrone. ")
    else:
        saildrone_data = read_shapefile(filedir=saildrone_shp_dir, product="saildrone")
        swhs = []
        sd_time = []
        filenames = []
        for num, fl in enumerate(satellite_shp_fls):
            print(num + 1, "/", len(satellite_shp_fls))
            data = read_swath(filename=f"{fl}.nc", product=config["satellite_product"])
            data_gpd = store_data_as_points(
                data=data, product=config["satellite_product"]
            )

            sd_subset = saildrone_data[
                (
                    data_gpd.Time.iloc[0]
                    - pd.Timedelta(minutes=config["saildrone_time_tolerance_min"])
                    <= saildrone_data.Time
                )
                & (
                    data_gpd.Time.iloc[0]
                    + pd.Timedelta(minutes=config["saildrone_time_tolerance_min"])
                    >= saildrone_data.Time
                )
                & (saildrone_data.geometry != None)
            ].reset_index(drop=True)
            if len(sd_subset) > 0:
                data_gpd["filename"] = fl
                swhs.append(data_gpd)
                sd_time.append(sd_subset.Time)
                filenames.append(fl)

        in_range = filenames
        not_in_range = [fl for fl in satellite_shp_fls if fl not in in_range]

        write_range_not_range_to_log(
            in_range=in_range, not_in_range=not_in_range, config=config, pass_number=2
        )
