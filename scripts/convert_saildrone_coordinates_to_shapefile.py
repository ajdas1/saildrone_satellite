from file_check import (
    read_config,
    check_for_saildrone_data,
    check_for_saildrone_shapefile,
)
from read_product import read_saildrone
from shapefile_geometry import convert_saildrone_coordinates_to_points, write_shapefile


config = read_config()

if not config["convert_saildrone_coordinates_to_shapefile"]:
    print("Skipping the conversion of saildrone coorindates to shapefile.")
else:
    print(
        f"Converting saildrone {config['saildrone_number']} "
        + f"from {config['saildrone_year']} coordinates to shapefile."
    )

    filename = check_for_saildrone_data(
        sd_number=config["saildrone_number"],
        sd_year=config["saildrone_year"],
        format=".nc",
    )
    filename_shapefile = check_for_saildrone_shapefile(
        sd_number=config["saildrone_number"],
        sd_year=config["saildrone_year"],
        format=".shp",
    )

    if len(filename_shapefile) > 0:
        if filename_shapefile in filename:
            print("This saildrone has already been processed.")
            exit()
    else:
        data = read_saildrone(filename=filename)
        data_gpd = convert_saildrone_coordinates_to_points(data=data)
        write_shapefile(data=data_gpd, product="saildrone", filename=filename)
