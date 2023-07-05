# saildrone_satellite


A good place to download satellite data granules: [NASA EARTHDATA](earthdata.nasa.gov) using their HITIDE4 API.



# To get the environment set up:

The modules used for running this package are stored in the top-level environment.yml file.

To create a new Conda environment with the provided modules (you only need to do this once), run the following from the top-level directory:

```
conda env create -f environment.yml
conda activate sd_satellite
conda develop "$PWD/util"
```

After this, any time you want to use the package, you just run `conda activate sd_satellite`.


# Workflow: 

There is a top-level **run.sh** script that performs the analysis sequence.

The parameters are controlled by the top-level **config.yaml** script.

Currently implemented analysis sequence:
- creating a data directory structure
- registering a dataset
- converting saildrone path to shapefile
- converting swath outlines to shapefiles
- matching saildrone time and region to swath shapefiles
- plotting saildrone data swath coverage

In progress:
- compare saildrone data to that of satellite swath

Currently able to process the following datasets:
- ASCAT
- SMAP