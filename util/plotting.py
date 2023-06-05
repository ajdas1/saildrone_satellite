import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import xarray as xr

from cartopy.feature import COASTLINE, LAND
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.gridspec import GridSpec
# from typing import List


proj = ccrs.PlateCarree(central_longitude = 0)

def set_cartopy_projection(
        ax: plt.Axes,
        extent: list[float] = [-180, 180, -90, 90],
        xticks: np.ndarray = np.arange(-180, 181, 30),
        yticks: np.ndarray = np.arange(-90, 91, 15),
        xlabel: str = "left",
        ylabel: str = "bottom",
):
    ax.add_feature(COASTLINE.with_scale('110m'), edgecolor="k")
    ax.set_extent(extent, crs=proj)

    plot_labels(ax=ax, xticks=xticks, yticks=yticks, xlabel=xlabel, ylabel=ylabel)



def plot_labels(
        ax: plt.Axes,
        xticks: np.array, yticks: np.array, 
        xlabel: str = "left", ylabel: str = "bottom", 
        ):
    
    gl = ax.gridlines(
        crs = proj,
        draw_labels = True,
        linewidth = 1,
        color = "gray",
        alpha = 1,
        linestyle = "--"
    )
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    if ylabel == "top":
        gl.top_labels = True
        gl.bottom_labels = False
    elif ylabel == "bottom":
        gl.top_labels = False
        gl.bottom_labels = True
    elif ylabel == "both":
        gl.top_labels = True
        gl.bottom_labels = True

    if xlabel == "left":
        gl.left_labels = True
        gl.right_labels = False
    elif xlabel == "right":
        gl.left_labels = False
        gl.right_labels = True
    elif xlabel == "both":
        gl.left_labels = True
        gl.right_labels = True


def plot_swath(
        data: xr.DataArray,
        variable: str = "swath", 
        plot_kwargs: dict = {"cmap": "turbo", "vmin": 0, "vmax": 20},
        cbar_kwargs: dict = {"ticks": np.arange(0, 21, 1), "label": "Wind speed (m/s)"},
        savefile: str = "test.png"
        ):

    start_time = data.time[0, 0].dt.strftime("%Y-%m-%d %H:%M:%S").values
    end_time = data.time[-1, -1].dt.strftime("%Y-%m-%d %H:%M:%S").values

    if variable == "swath":
        data_var = np.ones(data.lon.shape)
    else:
        data_var = data[variable]
    fig = plt.figure(figsize = (12, 5))
    gs = GridSpec(1, 2, width_ratios = [1, .03])
    gs.update(wspace=-0.2)
    ax = fig.add_subplot(gs[0, 0], projection=proj)
    cax = fig.add_subplot(gs[0, 1])
    f1 = ax.scatter(
        data.lon, data.lat, 1, c=data_var, 
        transform=proj, **plot_kwargs)
    _ = plt.colorbar(f1, cax=cax, **cbar_kwargs)
    set_cartopy_projection(ax=ax)
    ax.set_title(f"{start_time} UTC - {end_time} UTC")
    plt.savefig(savefile, dpi=200, bbox_inches="tight")
    plt.close("all")
