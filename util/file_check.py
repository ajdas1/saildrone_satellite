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






