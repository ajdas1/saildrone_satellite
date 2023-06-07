import os



def create_data_folder_structure():

    path = fetch_repo_path()

    if not os.path.isdir(f"{path}/data"):
        os.mkdir(f"{path}/data")
    
    if not os.path.isdir(f"{path}/data_shapefile"):
        os.mkdir(f"{path}/data_shapefile")





def register_new_dataset(product: str):

    path = fetch_repo_path()

    if not os.path.isdir(f"{path}/data/{product}"):
        os.mkdir(f"{path}/data/{product}")

    if not os.path.isdir(f"{path}/data_shapefile/{product}"):
        os.mkdir(f"{path}/data_shapefile/{product}")




def check_for_shapefile_data(product: str, append_datadir: bool = False) -> list[str]:

    path = fetch_repo_path()
    product_path = f"{path}/data_shapefile/{product}"

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path)])
        if append_datadir:
            files = [f"{path}/{fl}" for fl in files]

        return files
    

def check_for_product_data(product: str, format: str = ".nc", append_datadir: bool = False) -> list[str]:

    """
    files = check_for_product(datadir: str)

    Arguments:
    - datadir: directory where data files are located
    - format: what format should be looked for

    Returns:
    - files: list of files in directory with provided format
    """

    path = fetch_repo_path()
    product_path = f"{path}/data/{product}"

    if os.path.isdir(product_path):
        files = sorted([fl for fl in os.listdir(product_path) if format in fl])
        if append_datadir:
            files = [f"{path}/{fl}" for fl in files]

        return files



def fetch_repo_path():
    path = os.getcwd().split(os.sep)
    try: 
        sdp_idx = path.index("saildrone_satellite")
        return os.sep.join(path[:sdp_idx+1])
    except:
        print("Please run inside repository.")
        exit()




