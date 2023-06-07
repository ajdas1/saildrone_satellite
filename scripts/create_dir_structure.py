from file_check import create_data_folder_structure, read_config

config = read_config()

if not config["create_dir_structure"]:
    print("Skipping the creation of a data folder structure.")
else:
    print("Creating the directory structure for processing.")
    create_data_folder_structure()