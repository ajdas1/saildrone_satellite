from file_check import read_config, register_new_dataset
from read_product import DS


config = read_config()

if not config["register_dataset"]:
    print("Skipping the registration of a new satellite product.")
else:
    print(f"Registering a new dataset: {config['satellite_product']}")
    register_new_dataset(product=config["satellite_product"])

    supported_datasets = [e.value for e in DS]
    if config["satellite_product"] not in supported_datasets:
        print("The shapefile processing for this dataset has not yet been implemented.")
        print("You will need to add a processing step before continuing.")
