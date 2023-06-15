import pandas as pd
from file_check import (
    read_config,
    check_for_saildrone_shapefile,
    check_for_shapefile_data,
    write_range_not_range_to_log,
)
from read_product import read_shapefile, read_in_range_log, read_not_in_range_log
from shapefile_geometry import saildrone_intersect

config = read_config()

if not config["match_saildrone_satellite_swaths_pass1"]:
    print("Skipping matching saildrone data to satellite swaths - pass 1.")
else:
    print(
        f"First pass matching saildrone {config['saildrone_number']} "
        + f"from {config['saildrone_year']} to  "
        + f"{config['satellite_product']} satellite swaths."
    )

    saildrone_shp_dir = check_for_saildrone_shapefile(
        sd_number=config["saildrone_number"], sd_year=config["saildrone_year"]
    )
    satellite_shp_fls = check_for_shapefile_data(
        product=config["satellite_product"], append_datadir=False
    )
    fls_in_range = read_in_range_log(config=config, pass_number=1)
    fls_not_in_range = read_not_in_range_log(config=config, pass_number=1)
    satellite_shp_fls = [
        fl
        for fl in satellite_shp_fls
        if (fl not in fls_in_range) and (fl not in fls_not_in_range)
    ]

    if len(satellite_shp_fls) == 0:
        print("All the satellite swaths have already been compared to this saildrone. ")
    else:
        saildrone_data = read_shapefile(filedir=saildrone_shp_dir, product="saildrone")
        sat = []
        for num, fl in enumerate(satellite_shp_fls):
            print(num + 1, "/", len(satellite_shp_fls))
            tmp = read_shapefile(filedir=fl, product=config["satellite_product"])
            tmp["filename"] = fl
            sat.append(tmp)
        satellite_data = pd.concat(sat).reset_index(drop=True)

        satellite_data["SD_intersect"] = satellite_data.apply(
            saildrone_intersect, saildrone_data=saildrone_data, axis=1
        )

        sat_in_range = satellite_data[satellite_data.SD_intersect].reset_index(
            drop=True
        )
        sat_not_in_range = satellite_data[
            satellite_data.SD_intersect == False
        ].reset_index(drop=True)

        write_range_not_range_to_log(
            in_range=sat_in_range,
            not_in_range=sat_not_in_range,
            config=config,
            pass_number=1,
        )
