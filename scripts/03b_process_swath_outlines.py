

import file_check
import importlib
import read_product
import swath_geometry

from datetime import datetime
# from datetime import datetime

importlib.reload(file_check)
from file_check import check_for_product_data, check_for_shapefile_data

importlib.reload(read_product)
from read_product import DS, read_swath

importlib.reload(swath_geometry)
from swath_geometry import write_shapefile, create_swath_polygon

import sys

if len(sys.argv) > 1:
    product = sys.argv[1]
else:
    product = "ASCAT"
    # print("Please provide the product to be processed.")
    # exit()

data_files = check_for_product_data(product=product, format=".nc", append_datadir=False)
processed_files = check_for_shapefile_data(product=product, append_datadir=False)
print(f"There are {len(data_files)} files to process for the {product} dataset.")

if len(processed_files) > 0:
    print("Some files have already been processed. Only processing new files.")
    data_files = [df for df in data_files if df[:-3] not in processed_files]
    print(f"There are {len(data_files)} new files to process for the {product} dataset.")




if product not in [e.value for e in DS]:
    print("The processing for this dataset has not yet been defined.")
    print("Please do the following:")
    print("     - add a read_**dataset** function within read_product.py")
    print("     - assign the product name to the DS enum within read_product.py")
    exit()

else:
    for num, fl in enumerate(data_files):
        print(f"     Processing {num+1} / {len(data_files)}: {fl}", end="")
        stime = datetime.now()
        data = read_swath(filename=fl, product=product)
        data_gpd = create_swath_polygon(data=data, product=product)
        write_shapefile(data=data_gpd, product=product, filename=fl)
        etime = datetime.now()
        dt = etime - stime
        print(f" ({dt.total_seconds():.2f} seconds)")
