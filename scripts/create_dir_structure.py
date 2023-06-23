from file_check import create_data_folder_structure, read_config

config = read_config()

if config["create_dir_structure"]:
    print("Creating the directory structure for processing.")
    create_data_folder_structure()
