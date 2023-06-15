
import xarray as xr

from datetime import datetime

from read_product import read_swath

def subset_swath_time(data: xr.DataArray, start_time: datetime, end_time: datetime) -> xr.DataArray:

    data_pd = data.to_dataframe()
    data_subset = data_pd[(data_pd.time >= start_time) & (data_pd.time < end_time)]

    data_xr = data_subset.to_xarray()
    data_xr = data_xr.set_coords(["time", "lat", "lon"])

    return data_xr


def subset_files_in_time_range(
        files: list[str], start_time: datetime, end_time: datetime, 
        product: str, logfile: bool = True, 
        logpath: str = "/Users/asavarin/Desktop/work/saildrone_satellite/log"
        ) -> list[str]:

    files_in_time_range = []
    for fl in files:
        data = read_swath(filename=fl, product=product)
        subset_data = subset_swath_time(data=data, start_time=start_time, end_time=end_time)
        if len(subset_data.time) > 0:
            files_in_time_range.append(fl)
    
    if logfile:
        filename = f"{logpath}/sir_{product}_"
        filename += f"{start_time.strftime('%Y%m%d%H%M%S')}-"
        filename += f"{end_time.strftime('%Y%m%d%H%M%S')}.log"
        file = open(filename, "w")
        for line in files_in_time_range:
            file.write(line + "\n")
        file.close()

    return files_in_time_range


# def write_to_log_file(logfile: str):
