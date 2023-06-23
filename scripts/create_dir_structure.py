from read_write import create_data_folder_structure, read_config

config = read_config()

if not config["create_dir_structure"]:
    exit


print("Creating the directory structure for processing.")
create_data_folder_structure()
