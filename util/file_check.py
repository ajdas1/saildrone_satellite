import geopandas as gpd
import os
import yaml
import shutil

def fetch_repo_path():
    path = os.getcwd().split(os.sep)
    try: 
        sdp_idx = path.index("saildrone_satellite")
        return os.sep.join(path[:sdp_idx+1])
    except:
        print("Please run inside repository.")
        exit()






def read_config():
    config_file = f"{fetch_repo_path()}/config.yaml"

    with open(config_file) as fl:
        config = yaml.load(fl, Loader=yaml.FullLoader)

    return config



def create_data_folder_structure():

    config = read_config()
    path = fetch_repo_path()

    if not os.path.isdir(f"{path}/{config['satellite_data_folder']}"):
        os.mkdir(f"{path}/{config['satellite_data_folder']}")
    
    if not os.path.isdir(f"{path}/{config['shapefile_data_folder']}"):
        os.mkdir(f"{path}/{config['shapefile_data_folder']}")
    
    if not os.path.isdir(f"{path}/{config['saildrone_data_folder']}"):
        os.mkdir(f"{path}/{config['saildrone_data_folder']}")
        if not os.path.isdir(f"{path}/{config['saildrone_data_folder']}/nc"):
            os.mkdir(f"{path}/{config['saildrone_data_folder']}/nc")
        if not os.path.isdir(f"{path}/{config['saildrone_data_folder']}/shapefile"):
            os.mkdir(f"{path}/{config['saildrone_data_folder']}/shapefile")





def register_new_dataset(product: str):

    config = read_config()
    path = fetch_repo_path()

    if not os.path.isdir(f"{path}/{config['satellite_data_folder']}/{product}"):
        os.mkdir(f"{path}/{config['satellite_data_folder']}/{product}")

    if not os.path.isdir(f"{path}/{config['shapefile_data_folder']}/{product}"):
        os.mkdir(f"{path}/{config['shapefile_data_folder']}/{product}")




def check_for_shapefile_data(product: str, append_datadir: bool = False) -> list[str]:

    config = read_config()
    path = fetch_repo_path()
    product_path = f"{path}/{config['shapefile_data_folder']}/{product}"

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path)])
        if append_datadir:
            files = [f"{product_path}/{fl}" for fl in files]
    else:
        files = []

    return files



def check_for_saildrone_data(sd_number: int, sd_year: int, format: str = ".nc"):

    config = read_config()
    path = fetch_repo_path()
    sd_path = f"{path}/{config['saildrone_data_folder']}/nc"

    files = [fl for fl in os.listdir(sd_path) if str(sd_number) in fl and str(sd_year) in fl and format in fl]

    if len(files) == 1:
        return files[0]
    elif len(files) == 0:
        print("No saildrone data file.")
    else:
        print("More than one matching saildrone file.")
        

def check_for_saildrone_shapefile(sd_number: int, sd_year: int, format: str = ".nc"):

    config = read_config()
    path = fetch_repo_path()
    sd_path = f"{path}/{config['saildrone_data_folder']}/shapefile"

    files = [fl for fl in os.listdir(sd_path) if str(sd_number) in fl and str(sd_year) in fl]

    if len(files) == 1:
        return files[0]    
    else:
        files = []

    return files

        


def check_for_satellite_data(product: str, format: str = ".nc", append_datadir: bool = False) -> list[str]:

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
    product_path = f"{path}/{config['satellite_data_folder']}/{product}"

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path) if format in fl])
        if append_datadir:
            files = [f"{product_path}/{fl}" for fl in files]

        return files



def write_range_not_range_to_log(in_range: gpd.GeoDataFrame, not_in_range: gpd.GeoDataFrame, config: dict, pass_number: int = 1):
    path = fetch_repo_path()
    log_path_in_range = f"{path}/{config['log_data_folder']}/saildrone_{config['saildrone_number']}_{config['saildrone_year']}_{config['satellite_product']}_swath_in_range_pass{pass_number}.txt"
    log_path_not_in_range = f"{path}/{config['log_data_folder']}/saildrone_{config['saildrone_number']}_{config['saildrone_year']}_{config['satellite_product']}_swath_not_in_range_pass{pass_number}.txt"

    with open(log_path_in_range, "a") as fl:
        if isinstance(in_range, gpd.GeoDataFrame):
            for _, row in in_range.iterrows():
                fl.write(row.filename + "\n")
        elif isinstance(in_range, list):
            for row in in_range:
                fl.write(row + "\n")
                
    with open(log_path_not_in_range, "a") as fl:
        if pass_number == 2:
            fl_prev = f"{path}/{config['log_data_folder']}/saildrone_{config['saildrone_number']}_{config['saildrone_year']}_{config['satellite_product']}_swath_not_in_range_pass{pass_number-1}.txt"
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



