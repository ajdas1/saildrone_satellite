


import pandas as pd

from file_check import read_config, check_for_saildrone_data, fetch_repo_path, check_for_saildrone_shapefile
import importlib
import read_product
importlib.reload(read_product)
from read_product import read_shapefile, read_in_range_log, read_saildrone, read_swath
from shapefile_geometry import store_data_as_points
import plotting
importlib.reload(plotting)
from plotting import plot_saildrone_overlap_swath_general

config = read_config()


if not config["plot_saildrone_data_swath_coverage"]:
    print("Skipping plotting the saildone data swath coverage.")
else:
    print(
        f"Plotting the swath coverage of {config['saildrone_number']} from "
        + f"{config['saildrone_year']} to "
        + f"{config['satellite_product']} satellite swaths."
    )

    filename = check_for_saildrone_data(
        sd_number=config["saildrone_number"],
        sd_year=config["saildrone_year"],
        format=".nc",
    )    
    filename_shapefile = check_for_saildrone_shapefile(
        sd_number=config["saildrone_number"],
        sd_year=config["saildrone_year"],
    )
    satellite_shp_fls_match = read_in_range_log(config=config, pass_number=2)
    if len(satellite_shp_fls_match) == 0:
        print("There are no matching satellite swaths.")
    else:

        saildrone_data = read_saildrone(filename=filename, masked_nan=True)[config["saildrone_variable_name"]]
        data_units = saildrone_data.units
        saildrone_data = saildrone_data.to_dataframe().reset_index()

        sat = []
        for num, fl in enumerate(satellite_shp_fls_match):
            print(num + 1, "/", len(satellite_shp_fls_match))
            sat.append(read_shapefile(filedir=fl, product=config["satellite_product"])[["StartTime", "EndTime"]])
        satellite_swaths = pd.concat(sat).reset_index(drop=True)

        plot_saildrone_overlap_swath_general(
            saildrone_data=saildrone_data, 
            satellite_swaths=satellite_swaths, 
            data_units=data_units, 
            filename=f"SD{config['saildrone_number']}.{config['saildrone_year']}_{config['satellite_product']}_overlap.png"
        )


