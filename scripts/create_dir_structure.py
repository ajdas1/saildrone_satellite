from read_write import create_data_folder_structure, read_config
import sys

config = read_config()

if not config["create_dir_structure"]:
    sys.exit


print("Creating the directory structure for processing.")
create_data_folder_structure()
