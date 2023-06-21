import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
import pandas as pd
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



def plot_saildrone_overlap_swath_general(saildrone_data: pd.DataFrame, satellite_swaths: pd.DataFrame, data_units: str, filename: str):

    sd_months = saildrone_data.time.dt.month.unique()
    savedir = f"{fetch_repo_path()}{os.sep}{config['figure_data_folder']}"

    fig = plt.figure(figsize=(12, len(sd_months)*3))
    gs = GridSpec(len(sd_months), 1)
    gs.update(hspace=.25)
    axes = []
    for mon in range(len(sd_months)):
        if mon == 0:
            axes.append(fig.add_subplot(gs[mon, 0]))
        else:
            axes.append(fig.add_subplot(gs[mon, 0], sharey=axes[0]))
        axes[mon].grid(True, which="both", linewidth=.5, linestyle="dashed")

    for mon, month in enumerate(sd_months):
        sat_sub = satellite_swaths[(satellite_swaths.StartTime.dt.month == month) | (satellite_swaths.EndTime.dt.month == month)].reset_index(drop=True)
        if len(sat_sub) > 0:
            month_start = pd.to_datetime(f"{sat_sub.StartTime.dt.year.iloc[0]}{month:02d}01")
            sat_sub["tmfmt_start"] = pd.to_timedelta(sat_sub.StartTime - month_start).dt.total_seconds() / 60 / 60 / 24 + 1
            sat_sub["tmfmt_end"] = pd.to_timedelta(sat_sub.EndTime - month_start).dt.total_seconds() / 60 / 60 / 24 + 1
            for idx in range(sat_sub.index[0], sat_sub.index[-1]+1, 1):
                axes[mon].axvspan(sat_sub.tmfmt_start.iloc[idx], sat_sub.tmfmt_end.iloc[idx], alpha=.3, color="k")

        sd_sub = saildrone_data[saildrone_data.time.dt.month == month].reset_index(drop=True)
        if len(sd_sub) > 0:
            sd_sub["tmfmt"] = pd.to_timedelta(sd_sub.time - sd_sub.time.iloc[0]).dt.total_seconds() / 60 / 60 / 24 + 1
            axes[mon].plot(sd_sub.tmfmt, sd_sub[config["saildrone_variable_name"]], ".", markersize=1)
            axes[mon].set_xticks(np.arange(1, sd_sub.tmfmt.max(), 1), minor=True)
            axes[mon].set_xticks(np.arange(1, sd_sub.tmfmt.max(), 5), minor=False)
            axes[mon].set_xlim(1, 32)
            axes[mon].set_title(f"SD: {config['saildrone_number']} ({config['saildrone_year']}); Swath: {config['satellite_product']}; Variable: {config['saildrone_variable_name']} ({data_units}); Month: {month}")


    axes[0].axvspan(-10, 0, alpha=.3, color="k", label="Swath overlap")
    axes[0].plot(-10, 0, ".", markersize=1, label="Saildrone")
    axes[0].legend(loc=2)
    axes[-1].set_xlabel("Day of month")

    plt.savefig(f"{savedir}{os.sep}{filename}", dpi=200, bbox_inches="tight")
    plt.close("all")
