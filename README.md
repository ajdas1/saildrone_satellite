# saildrone_satellite


A good place to download satellite data granules: [NASA EARTHDATA](earthdata.nasa.gov) using their HITIDE4 API.





# Workflow: 

There is a top-level **run.sh** script that performs the analysis sequence.

The parameters are controlled by the top-level **config.yaml** script.

Currently implemented analysis sequence:
- creating a data directory structure
- registering a dataset
- converting swath outlines to shapefiles

In progress:
- converting saildrone path to shapefiles
- matching saildrone time and region to swath shapefiles

Currently able to process the following datasets:
- ASCAT