
import sys

from plot import (
    plot_timeseries_swath_overlap,
)
from read_write import (
    check_for_saildrone_data,
    read_config,
    read_in_range_log,
    read_matching_data_from_file,
    read_saildrone,
)


config = read_config()


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


