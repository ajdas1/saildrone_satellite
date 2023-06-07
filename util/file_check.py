import os
import yaml

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






