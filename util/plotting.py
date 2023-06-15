import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
import xarray as xr

from cartopy.feature import COASTLINE
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from file_check import fetch_repo_path, read_config
from matplotlib.gridspec import GridSpec


config = read_config()
proj = ccrs.PlateCarree(central_longitude=0)


def set_cartopy_projection(
    ax: plt.Axes,
    extent: list[float] = [-180, 180, -90, 90],
    xticks: np.ndarray = np.arange(-180, 181, 30),
    yticks: np.ndarray = np.arange(-90, 91, 15),
    xlabel: str = "bottom",
    ylabel: str = "left",
):
    """
    set_cartopy_projection()

    Arguments:
    - ax: the matplotlib axis to be used - must have a projection keyword
    - extent: longitude and latitude bounds
    - xticks: list or array of ticks for the x axis
    - yticks: list or array of ticks for the y axis
    - xlabel (left or right) - which side to label x-axis on
    - ylabel (left or right) - which side to label y-axis on

    Returns: None

    Adds the coastline, sets the extent of the map and grid lines.
    """
    ax.add_feature(COASTLINE.with_scale("110m"), edgecolor="k")
    ax.set_extent(extent, crs=proj)

    plot_labels(ax=ax, xticks=xticks, yticks=yticks, xlabel=xlabel, ylabel=ylabel)


def plot_labels(
    ax: plt.Axes,
    xticks: np.array,
    yticks: np.array,
    xlabel: str = "left",
    ylabel: str = "bottom",
):
    """
    plot_labels()

    Arguments:
    - ax: the matplotlib axis to be used - must have a projection keyword
    - xticks: list or array of ticks for the x axis
    - yticks: list or array of ticks for the y axis
    - xlabel (left or right) - which side to label x-axis on
    - ylabel (left or right) - which side to label y-axis on

    Returns: None

    Plots and labels the grid lines on the map.
    """
    gl = ax.gridlines(
        crs=proj, draw_labels=True, linewidth=1, color="gray", alpha=1, linestyle="--"
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
    savefile: str = "test.png",
):
    """
    plot_swath(data: xr.DataArray, variable: str, plot_kwargs: dict,
        cbar_kwargs: dict, saveflie: str)

    Arguments:
    - data: data array that contains coordinates and data
    - variable: name of the variable within the data array to be plotted
    - plot_kwargs: setting the color map and its limits
    - cbar_kwargs: setting the colorbar ticks and label
    - savefile: file to save the image in

    Returns: None

    Plots data from a satellite swath on a map.
    """
    repo_path = fetch_repo_path()
    plot_path = f"{repo_path}{os.sep}" + f"{config['figure_data_folder']}"

    start_time = data.time[0, 0].dt.strftime("%Y-%m-%d %H:%M:%S").values
    end_time = data.time[-1, -1].dt.strftime("%Y-%m-%d %H:%M:%S").values

    if variable == "swath":
        data_var = np.ones(data.lon.shape)
    else:
        data_var = data[variable]
    fig = plt.figure(figsize=(12, 5))
    gs = GridSpec(1, 2, width_ratios=[1, 0.03])
    gs.update(wspace=-0.2)
    ax = fig.add_subplot(gs[0, 0], projection=proj)
    cax = fig.add_subplot(gs[0, 1])
    f1 = ax.scatter(data.lon, data.lat, 1, c=data_var, transform=proj, **plot_kwargs)
    _ = plt.colorbar(f1, cax=cax, **cbar_kwargs)
    set_cartopy_projection(ax=ax)
    ax.set_title(f"{start_time} UTC - {end_time} UTC")
    plt.savefig(f"{plot_path}{os.sep}{savefile}", dpi=200, bbox_inches="tight")
    plt.close("all")
