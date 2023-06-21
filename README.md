# saildrone_satellite


A good place to download satellite data granules: [NASA EARTHDATA](earthdata.nasa.gov) using their HITIDE4 API.



# To get everything working:

The modules used for running this package are stored in the top-level environment.yml file.

To create a new Conda environment with the provided modules, run the following from the top-level directory:

```
conda env create -f environment.yml
conda activate sd_satellite
conda develop "$PWD/util"
```



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