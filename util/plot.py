
import os
import pandas as pd
from read_write import fetch_repo_path, read_config
import numpy as np
import matplotlib.pyplot as plt


from matplotlib.gridspec import GridSpec


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
            sd_sub["tmfmt"] = pd.to_timedelta(sd_sub.time - sd_sub.time.iloc[0]).dt.total_seconds() / 60 / 60 / 24 + 1
            if len(st_sub) > 0:
                st_sub["dt_tmfmt"] = pd.to_timedelta(st_sub.st_time - st_sub.sd_time).dt.total_seconds() / 60 / 60 / 24
                st_sub["sd_tmfmt"] = pd.to_timedelta(st_sub.st_time - sd_sub.time.iloc[0]).dt.total_seconds() / 60 / 60 / 24 + 1
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




def plot_scatterplot_overlap(combined_pts: pd.DataFrame, mean_pts: pd.DataFrame, nearest_pts: pd.DataFrame, filename: str, axmin=0, axmax=20):

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

    cbar = plt.colorbar(f1, cax=cax, orientation="horizontal")
    ax1.set_xlim(axmin, axmax)
    ax1.set_ylim(axmin, axmax)
    ax1.set_title("All points")
    ax2.set_title("Mean satellite point")
    ax3.set_title("Nearest satellite point")
    ax1.set_ylabel(f"Satellite {config['saildrone_variable_name']}")
    plt.savefig(f"{savedir}/{filename}", dpi=300, bbox_inches="tight")
    plt.close("all")

