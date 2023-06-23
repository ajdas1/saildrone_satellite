from read_write import DS, read_config, register_new_dataset

config = read_config()

if not config["register_dataset"]:
    exit()

print(f"Registering a new dataset: {config['satellite_product']}")
register_new_dataset()

supported_datasets = [e.value for e in DS]
if config["satellite_product"] not in supported_datasets:
    print("     The processing for this dataset has not yet been implemented.")
    print("     You will need to add a processing step before continuing.")
