from file_check import register_new_dataset
import importlib
import read_product
importlib.reload(read_product)
from read_product import DS

import sys





if len(sys.argv) > 1:
    print(f"\nRegistering {sys.argv[1]}")
    register_new_dataset(product=sys.argv[1])
else:
    print("\nPlease provide a dataset name to register.")

supported_datasets = [e.value for e in DS]
print()
print()
print("The currently supported datasets for later processing include:")
print("\n".join([f"   - {ds}" for ds in supported_datasets]))
print()
print("If your dataset is not included, you will need to add a processing step.\n")