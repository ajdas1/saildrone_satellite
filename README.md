# saildrone_satellite


A good place to download satellite data granules: [NASA EARTHDATA](earthdata.nasa.gov) using their HITIDE4 API.





# Workflow: 

When first downloading the repository, you can set up the data directories by calling:
** 01_create_directory_structure.py **
This will create the data structure needed to run the processing scripts.

After that is done, you can create a directory structure for a new dataset by calling:
** 02_register_dataset.py DATASET **
This will create directories that will be needed to process a specific dataset.

Move the swath data into the 