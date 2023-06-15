import geopandas as gpd
import os
import yaml


def fetch_repo_path():
    """
    fetch_repo_path

    Returns:
    - the path to the top-level repository directory.
    """
    path = os.getcwd().split(os.sep)
    try:
        sdp_idx = path.index("saildrone_satellite")
        return os.sep.join(path[: sdp_idx + 1])
    except:
        print("Please run inside repository.")
        exit()


def read_config() -> dict:
    """
    config = read_config()

    Returns:
    - the config dictionary read from the top-level config file.
    """
    config_file = f"{fetch_repo_path()}{os.sep}config.yaml"

    with open(config_file) as fl:
        config = yaml.load(fl, Loader=yaml.FullLoader)

    return config


def create_data_folder_structure():
    """
    create_data_folder_structure()

    Returns: None
    Creates the directory structure needed for the later steps to run properly.
    It creates the data folders for:
    - satellite data
    - shapefiles of satellite data
    - log files for swath overlap classification with saildrone
    - saildrone data

    The names of the directories can be changed in the top-level config,
    under filename setup.
    If the directories already exist, nothing is done.
    """
    config = read_config()
    path = fetch_repo_path()

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['satellite_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['satellite_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['shapefile_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['shapefile_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['log_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['log_data_folder']}")

    if not os.path.isdir(f"{path}{os.sep}" + f"{config['saildrone_data_folder']}"):
        os.mkdir(f"{path}{os.sep}" + f"{config['saildrone_data_folder']}")
        if not os.path.isdir(
            f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"
        ):
            os.mkdir(
                f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"
            )
        if not os.path.isdir(
            f"{path}{os.sep}"
            + f"{config['saildrone_data_folder']}{os.sep}"
            + f"shapefile"
        ):
            os.mkdir(
                f"{path}{os.sep}"
                + f"{config['saildrone_data_folder']}{os.sep}"
                + f"shapefile"
            )


def register_new_dataset(product: str):
    """
    register_new_dataset(product: str)

    Arguments:
    - product - the satellite product to be registered.

    Registering a product creates an empty directory for that dataset within
    data_satellite, where you put the downloaded data.
    It also creates a directory for the processed shapefiles belonging to
    that dataset.
    If the directory already exists, nothing is done.
    """
    config = read_config()
    path = fetch_repo_path()

    if not os.path.isdir(
        f"{path}{os.sep}" + f"{config['satellite_data_folder']}{os.sep}" + f"{product}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['satellite_data_folder']}{os.sep}"
            + f"{product}"
        )

    if not os.path.isdir(
        f"{path}{os.sep}" + f"{config['shapefile_data_folder']}{os.sep}" + f"{product}"
    ):
        os.mkdir(
            f"{path}{os.sep}"
            + f"{config['shapefile_data_folder']}{os.sep}"
            + f"{product}"
        )


def check_for_shapefile_data(product: str, append_datadir: bool = False) -> list[str]:
    """
    files = check_for_shapefile_data(product: str, append_datadir: bool = False)

    Arguments:
    - product - the satellite product in question.
    - append_datadir - whether the full path to the directory should be output.

    Returns:
    - a list of files within the shapefile data folder for that product.
    """

    config = read_config()
    path = fetch_repo_path()
    product_path = (
        f"{path}{os.sep}" + f"{config['shapefile_data_folder']}{os.sep}" + f"{product}"
    )

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path)])
        if append_datadir:
            files = [f"{product_path}{os.sep}" + f"{fl}" for fl in files]
    else:
        files = []

    return files


def check_for_saildrone_data(sd_number: int, sd_year: int, format: str = ".nc"):
    """
    files = check_for_saildrone_data(sd_number: int, sd_year: int, format: str = ".nc")

    Arguments:
    - sd_number: saildrone number.
    - sd_year: saildrone year.
    - format: format of saildrone data.

    Returns:
    - the filename for the saildrone data.

    Currently, only .nc format is supported, and the file name should
    contain the saildrone year and number.
    """
    config = read_config()
    path = fetch_repo_path()
    sd_path = f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "nc"

    files = [
        fl
        for fl in os.listdir(sd_path)
        if str(sd_number) in fl and str(sd_year) in fl and format in fl
    ]

    if len(files) == 1:
        return files[0]
    elif len(files) == 0:
        print("No saildrone data file.")
    else:
        print("More than one matching saildrone file.")


def check_for_saildrone_shapefile(sd_number: int, sd_year: int):
    """
    files = check_for_saildrone_data(sd_number: int, sd_year: int)

    Arguments:
    - sd_number: saildrone number.
    - sd_year: saildrone year.

    Returns:
    - the filename for the saildrone shalefile data directory.
    """
    config = read_config()
    path = fetch_repo_path()
    sd_path = (
        f"{path}{os.sep}" + f"{config['saildrone_data_folder']}{os.sep}" + "shapefile"
    )

    files = [
        fl for fl in os.listdir(sd_path) if str(sd_number) in fl and str(sd_year) in fl
    ]

    if len(files) == 1:
        files = files[0]
    else:
        files = []

    return files


def check_for_satellite_data(
    product: str, format: str = ".nc", append_datadir: bool = False
) -> list[str]:
    """
    files = check_for_product(datadir: str)

    Arguments:
    - datadir: directory where data files are located
    - format: what format should be looked for

    Returns:
    - files: list of files in directory with provided format
    """

    config = read_config()
    path = fetch_repo_path()
    product_path = (
        f"{path}{os.sep}" + f"{config['satellite_data_folder']}{os.sep}" + f"{product}"
    )

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path) if format in fl])
        if append_datadir:
            files = [f"{product_path}{os.sep}" + f"{fl}" for fl in files]

        return files


def write_range_not_range_to_log(
    in_range: gpd.GeoDataFrame,
    not_in_range: gpd.GeoDataFrame,
    config: dict,
    pass_number: int = 1,
):
    """
    write_range_not_range_to_log(in_range: list, gpd.GeoDataFrame,
    not_in_range: list, gpd.GeoDataFrame, config: dict, pass_number: int = 1,)

    Arguments:
    - in_range: list or geodataframe with swaths in range of the saildrone.
    - not_range: list or geodataframe with swaths not in range of the saildrone.
    - config: the configuration dictionary from top-level config file.
    - pass_number: matching for only space (1) or time and space (2).

    Returns: None

    Writes the filenames of swaths in range of the saildrone to file.
    If pass_number = 1, it matches the entire swath time to saildrone location.
    If pass_number = 2, it matches a shorter time window to saildrone location.
    The time window tolerance is specified in the top-level config, in minutes
    (saildrone_time_tolerance_min) - it looks x min ahead and behind the saildrone).
    """
    path = fetch_repo_path()
    log_path_in_range = (
        f"{path}{os.sep}"
        + f"{config['log_data_folder']}{os.sep}"
        + f"saildrone_{config['saildrone_number']}_"
        + f"{config['saildrone_year']}_"
        + f"{config['satellite_product']}_"
        + f"swath_in_range_pass{pass_number}.txt"
    )
    log_path_not_in_range = (
        f"{path}{os.sep}"
        + f"{config['log_data_folder']}{os.sep}"
        + f"saildrone_{config['saildrone_number']}_"
        + f"{config['saildrone_year']}_"
        + f"{config['satellite_product']}_"
        + f"swath_not_in_range_pass{pass_number}.txt"
    )

    with open(log_path_in_range, "a") as fl:
        if isinstance(in_range, gpd.GeoDataFrame):
            for _, row in in_range.iterrows():
                fl.write(row.filename + "\n")
        elif isinstance(in_range, list):
            for row in in_range:
                fl.write(row + "\n")

    with open(log_path_not_in_range, "a") as fl:
        if pass_number == 2:
            fl_prev = (
                f"{path}{os.sep}"
                + f"{config['log_data_folder']}{os.sep}"
                + f"saildrone_{config['saildrone_number']}_"
                + f"{config['saildrone_year']}_"
                + f"{config['satellite_product']}_"
                + f"swath_not_in_range_pass{pass_number-1}.txt"
            )
            with open(fl_prev, "r") as fl_p:
                data = fl_p.readlines()
            with open(log_path_not_in_range, "w") as fl:
                for line in data:
                    fl.write(line)

        if isinstance(not_in_range, gpd.GeoDataFrame):
            for _, row in not_in_range.iterrows():
                fl.write(row.filename + "\n")
        elif isinstance(not_in_range, list):
            for row in not_in_range:
                fl.write(row + "\n")
