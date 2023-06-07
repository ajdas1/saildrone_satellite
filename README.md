# saildrone_satellite


A good place to download satellite data granules: [NASA EARTHDATA](earthdata.nasa.gov) using their HITIDE4 API.





# Workflow: 

When first downloading the repository, you can set up the data directories by calling:
** 01_create_directory_structure.py **
This will create the data structure needed to run the processing scripts.

After that is done, you can create a directory structure for a new dataset by calling:
** 02_register_dataset.py DATASET **
This will create directories that will be needed to process a specific dataset.

Move the swath data into the newly created directory under **/data/DATASET**

There are a number of steps to data processing (expained in more detail later):
1. extract point coordinates from the Saildrone data ** 03a_process_saildrone_coordinates.py ** (only run once per saildrone) -> shapefiles
2. extract swath outlines from each provided data file ** 03a_process_swath_outlines.py ** (run whenever you add new data) -> shapefiles
3. match the locations of saildrone and satellite swath ** 04_match_saildrone_swath_locations.py ** (run whenever you add new data) -> list of matching data files 
