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


# To implement a new dataset:

Let's say the new dataset is called "ABC", and it contains sea surface temperature data. The additions you need to make are to the `read_write.py` script inside `./util`.

- inside `class DS(Enum)`, add the name (e.g., `ABC = "ABC"`)
- inside `def read_swath(...)`, copy one of the `if product == ...` sections and edit the new one for your dataset:

```
if product == DS.ABC.value:
    current_filename = ... (remains unchanged)
    data = read_ABC(filename=current_filename, masked_nan=masked_nan)
```

- copy one of the previous functions (e.g., `read_ASCAT`) and edit it to reflect the new satellite product. Among other things, you will need to:
    - rename any latitude variable (Latitude, Lat, latitude) to lat
    - rename any longitude variable (Longitude, Long, Lon, longitude, long) to lon
    - rename any time variable to time (Time, Date, date) to time
    - drop any unneeded variables to speed up processing
    - if longitude is defined from [0, 360), convert it to [-180, 180) to match the saildrone

```
def read_ABC(filename: str, masked_nan: bool = False) -> xr.DataArray:
    """ ... """

    data = xr.open_dataset(
        filename,
        engine="netcdf4",
        mask_and_scale=True,
        decode_times=True,
        decode_coords=True,
        drop_variables=[...], 
    )
    # (drop variables should contain list of variables to ignore - speeds up processing)

    # if you want to rename variables (e.g., so they match saildrone ...), do that here
    data = data.rename(
        {
            "lat...": "lat",
            "lon...": "lon",
            "time...": "time",
            "sea_surface_temperature": "sst,
            ...
        }
    )

    # if not already, convert longitude so it goes from -180 to 180
    # data.coords["lon"] = (data.coords["lon"] + 180) % 360 - 180

    # set the time coordinate
    data = data.set_coords(["time"]) # replace with name for time coordinate

    if masked_nan:
        data_df = data.to_dataframe().reset_index(drop=True)
        masked_data = data_df[data_df.lon.notna() & data_df.lat.notna()]
        masked_data = masked_data.dropna(axis=0, thresh=4)
        masked_data = masked_data.set_index("time")
        masked_data["lat"] = masked_data["lat"].round(decimals=2)
        masked_data["lon"] = masked_data["lon"].round(decimals=2)
        data = masked_data.to_xarray()
        data = data.set_coords(["lat", "lon"])

    return data
```

- save the changes, remove the `./util/__pycache__` directory so that the changes will take effect
- in `./config.yaml`, edit the `satellite_product` and `satellite_variable_name` to match 
```
# satellite dataset setup
satellite_product = "ABC"
satellite_variable_name = "sst" (whatever you renamed your variable to in the read_ABC function)

saildrone_variable_name = "air_temperature (whatever the corresponding saildrone variable name is)
```

- run
```
./run.sh (if using bash)
OR
python ./scripts/match_saildrone_satellite_swaths.py
```