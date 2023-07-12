
import os
import pandas as pd
from read_write import fetch_repo_path, read_config
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from cartopy.feature import COASTLINE, LAND
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from typing import List


def plot_timeseries_swath_overlap(sd_data: pd.DataFrame, swath_match: pd.DataFrame, filename: str):

    config = read_config()
    savedir = f"{fetch_repo_path()}{os.sep}{config['figure_data_folder']}"
    sd_months = sd_data.time.dt.month.unique()

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

        sd_sub = sd_data[sd_data.time.dt.month == month].reset_index(drop=True)
        st_sub = swath_match[swath_match.sd_time.dt.month == month].reset_index(drop=True)
        if len(sd_sub) > 0:
            start_of_month = sd_sub.time.iloc[0].replace(day=1, hour=0, minute=0, second=0)
            sd_sub["tmfmt"] = pd.to_timedelta(sd_sub.time - start_of_month).dt.total_seconds() / 60 / 60 / 24 + 1
            if len(st_sub) > 0:
                st_sub["dt_tmfmt"] = pd.to_timedelta(st_sub.st_time - st_sub.sd_time).dt.total_seconds() / 60 / 60 / 24
                st_sub["sd_tmfmt"] = pd.to_timedelta(st_sub.st_time - start_of_month).dt.total_seconds() / 60 / 60 / 24 + 1
                st_sub["st_tmfmt"] = st_sub.sd_tmfmt + st_sub.dt_tmfmt
                for pt in range(len(st_sub)):
                    axes[mon].axline((st_sub.sd_tmfmt.iloc[pt], 0), (st_sub.st_tmfmt.iloc[pt], 1), lw=.2, c="k")

            axes[mon].plot(sd_sub.tmfmt, sd_sub[config["saildrone_variable_name"]], ".", markersize=1)
            axes[mon].set_xticks(np.arange(1, sd_sub.tmfmt.max(), 1), minor=True)
            axes[mon].set_xticks(np.arange(1, sd_sub.tmfmt.max(), 5), minor=False)
            axes[mon].set_xlim(1, 32)
            axes[mon].set_title(f"SD: {config['saildrone_number']} ({config['saildrone_year']}); Swath: {config['satellite_product']}; Variable: {config['saildrone_variable_name']}; Month: {month}")


    plt.savefig(f"{savedir}/{filename}", dpi=200, bbox_inches="tight")
    plt.close()




def plot_scatterplot_overlap(combined_pts: pd.DataFrame, mean_pts: pd.DataFrame, nearest_pts: pd.DataFrame, filename: str, axmin: float = 0, axmax: float = 20, linreg: bool = True):
    axmin = 0
    axmax = np.ceil(max(combined_pts.sd_var.max(), combined_pts.st_var.max())+2)
    config = read_config()
    savedir = f"{fetch_repo_path()}{os.sep}{config['figure_data_folder']}"
    fig = plt.figure(figsize = (12, 4.5))
    gs = GridSpec(2, 3, height_ratios=[1, .08])
    gs.update(hspace=.35)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1], sharex=ax1, sharey=ax1)
    ax3 = fig.add_subplot(gs[0, 2], sharex=ax1, sharey=ax1)
    cax = fig.add_subplot(gs[1, :])
    for ax in [ax1, ax2, ax3]:
        ax.grid(True, which="both", linewidth=.5, linestyle="dashed")
        ax.axline((0, 0), (1, 1), zorder=0, c="k", lw=1)
        ax.set_xlabel(f"SD {config['saildrone_variable_name']}")

    f1 = ax1.scatter(combined_pts.sd_var, combined_pts.st_var, s=15, c=combined_pts.dist, vmin=0, vmax=config["saildrone_distance_tolerance_km"], cmap="turbo_r", edgecolor="k", linewidth=.5)
    ax2.scatter(mean_pts.sd_var, mean_pts.st_var, s=15, c=mean_pts.dist, vmin=0, vmax=config["saildrone_distance_tolerance_km"], cmap="turbo_r", edgecolor="k", linewidth=.5)
    ax3.scatter(nearest_pts.sd_var, nearest_pts.st_var, s=15, c=nearest_pts.dist, vmin=0, vmax=config["saildrone_distance_tolerance_km"], cmap="turbo_r", edgecolor="k", linewidth=.5)
    ax1.set_yticks(ax1.get_xticks())

    if linreg:
        if len(combined_pts) >= 5:
            reg_combined = LinearRegression().fit(combined_pts.sd_var.values.reshape(-1, 1), combined_pts.st_var.values.reshape(-1, 1))
            reg_mean = LinearRegression().fit(mean_pts.sd_var.values.reshape(-1, 1), mean_pts.st_var.values.reshape(-1, 1))
            reg_nearest = LinearRegression().fit(nearest_pts.sd_var.values.reshape(-1, 1), nearest_pts.st_var.values.reshape(-1, 1))

            ax1.axline((0, reg_combined.intercept_[0]), slope=reg_combined.coef_[0][0], c="m", lw=1)
            ax2.axline((0, reg_mean.intercept_[0]), slope=reg_mean.coef_[0][0], c="m", lw=1)
            ax3.axline((0, reg_nearest.intercept_[0]), slope=reg_nearest.coef_[0][0], c="m", lw=1)

            txt = f"Slope: {reg_combined.coef_[0][0]:.2f}\nIntercept: {reg_combined.intercept_[0]:.2f}\nR" + u"$^2$" + f": {r2_score(combined_pts.sd_var, combined_pts.st_var):.2f}"
            ax1.text(axmin+.1, axmax-.1, txt, ha="left", va="top")
            txt = f"Slope: {reg_mean.coef_[0][0]:.2f}\nIntercept: {reg_mean.intercept_[0]:.2f}\nR" + u"$^2$" + f": {r2_score(mean_pts.sd_var, mean_pts.st_var):.2f}"
            ax2.text(axmin+.1, axmax-.1, txt, ha="left", va="top")
            txt = f"Slope: {reg_nearest.coef_[0][0]:.2f}\nIntercept: {reg_nearest.intercept_[0]:.2f}\nR" + u"$^2$" + f": {r2_score(nearest_pts.sd_var, nearest_pts.st_var):.2f}"
            ax3.text(axmin+.1, axmax-.1, txt, ha="left", va="top")

    _ = plt.colorbar(f1, cax=cax, orientation="horizontal", label="Distance between SD and sat point (km)")
    ax1.set_xticks(np.arange(0, 101, 5))
    ax1.set_yticks(ax1.get_xticks())
    ax1.set_xlim(axmin, axmax)
    ax1.set_ylim(axmin, axmax)
    ax1.set_title(f"All points (n={len(combined_pts)})")
    ax2.set_title(f"Mean satellite point (n={len(mean_pts)})")
    ax3.set_title(f"Nearest satellite point (n={len(nearest_pts)})")
    ax1.set_ylabel(f"Satellite {config['saildrone_variable_name']}")
    plt.savefig(f"{savedir}/{filename}", dpi=300, bbox_inches="tight")
    plt.close("all")






proj = ccrs.PlateCarree(central_longitude = 0)

def set_cartopy_projection_atlantic(
        ax: plt.Axes,
        extent: List[float] = [-111, 11, -5, 55],
        xticks: np.ndarray = np.arange(-120, 30, 10),
        yticks: np.ndarray = np.arange(-10, 61, 10),
        ylabel: str = "top"
    ):
    #ax.coastlines(color="k", zorder=1)
    ax.add_feature(COASTLINE.with_scale('10m'), edgecolor="k")
    ax.add_feature(LAND.with_scale('10m'), facecolor='.8')
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
    else:
        gl.top_labels = False

    if ylabel == "bottom":
        gl.bottom_labels = True
    else:
        gl.bottom_labels = False
    gl.right_labels = False

    ax.set_extent(extent, crs=proj)



def plot_matching_point_locations(match_data: list, sd_fls: list, extent: list = [-100, -50, 10, 40], filename: str = "test.png", title: str = ""):

    config = read_config()
    savedir = f"{fetch_repo_path()}{os.sep}{config['figure_data_folder']}"
    unique_sd_files = sorted(list(set(sd_fls)))
    cols = plt.cm.brg(np.linspace(0, 1, len(unique_sd_files)))

    fig = plt.figure(figsize = (10, 6))
    ax = fig.add_subplot(111, projection=proj)

    for sdfl in sd_fls:
        sd_col = unique_sd_files.index(sdfl)
        match_data_sd = match_data[sdfl]
        if len(match_data_sd) == 0:
            continue
        for swth in range(len(match_data_sd)):
            ax.plot([match_data_sd[swth].sd_lon, match_data_sd[swth].st_lon], [match_data_sd[swth].sd_lat, match_data_sd[swth].st_lat], c=cols[sd_col], lw=.5)

    for col in range(len(cols)):
        ax.plot([0, 0], [0, 1], c=cols[col], label=unique_sd_files[col][:11])
    _ = ax.legend(loc=3, ncol=4, mode="expand")

    ax.set_title(title)
    set_cartopy_projection_atlantic(ax=ax, extent=extent, ylabel="bottom")
    plt.savefig(f"{savedir}{os.sep}{filename}")
    plt.close("all")