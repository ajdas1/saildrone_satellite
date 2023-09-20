import cartopy.crs as ccrs
from cartopy.feature import COASTLINE, LAND
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import numpy as np
import matplotlib.pyplot as plt

#importing Satellite file
filename = 'C:/Users/Madeline/Documents/Projects/Hollings Summer PMEL/Python_Code/Workflow_SST_Interpolation/2021_work/cropped_POI_GHRSST_20210823000000.nc'

from netCDF4 import Dataset
data = Dataset(filename, "r")

#Getting variables from Satellite file
lon = data["lon"][:]
lat = data["lat"][:]
sst = data["quality_level"][0]



# filename_sd = 'C:\Users\Madeline\Desktop\Excel_Books for Saildrone\sd1045_POI_notime_20210823000000.csv'

# data_sd = Dataset(filename, "r")
# #Getting variables
# lon = data["Lon"]
# lat = data["Lat"]
# sst = data["Saildrone_SST"]



xticks = np.arange(-100, -49, 5) #every 5 deg
yticks = np.arange(0, 51, 5)  #
extent = [-85, -55, 15, 30]

proj = ccrs.PlateCarree(central_longitude=0)

fig = plt.figure(figsize = (10, 5))
ax = fig.add_subplot(111, projection=proj)


ax.add_feature(COASTLINE.with_scale("10m"), edgecolor="k")
ax.add_feature(LAND.with_scale("10m"), facecolor=".8")

#Adding contour map 
f1 = ax.contourf(lon, lat, sst, levels=np.arange(0, 6, 1), cmap="turbo", vmin=0, vmax=6)
cbar = plt.colorbar(f1, label="Quality Level", ticks=np.arange(0, 6, 1))

sd_lon = -65.5392586666666
sd_lat = 22.6734592
sd_sst = 28.5876
ax.scatter(sd_lon, sd_lat, s=100, edgecolor="k")

gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=1, color="gray", alpha=1, linestyle="--")
gl.xlocator = mticker.FixedLocator(xticks)
gl.ylocator = mticker.FixedLocator(yticks)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
ax.set_extent(extent, crs=proj)

gl.top_labels = False
gl.right_labels = False

plt.savefig("testthird2_QC.png", dpi=200, bbox_inches="tight")
plt.close("all")



