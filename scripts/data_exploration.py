

import importlib

import file_check
importlib.reload(file_check)
from file_check import check_for_product

import read_product
importlib.reload(read_product)
from read_product import read_swath

import plotting
importlib.reload(plotting)
from plotting import plot_swath


########### workflow
product = "ASCAT"

datadir = "/Users/asavarin/Desktop/work/saildrone_satellite/data"
savedir = "/Users/asavarin/Desktop/work/saildrone_satellite/figs/test"
datadir += f"/{product}"
files = check_for_product(datadir=datadir, format = ".nc")

# for fl in files:

#     data = read_swath(filename=f"{datadir}/{fl}", product=product)
    # plot_swath(data=data, variable="wind_speed", savefile=f"{savedir}/{fl}.png")
