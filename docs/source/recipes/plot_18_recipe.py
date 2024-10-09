"""
Plot to compare two linked datasets: Snow against Elevation
===========================================================

In this recipe, we will plot a dependant variable (in this example snow
cover) against an independent variable (elevation). This will be on a
contour plot separately and together, then finding the coefficient of
correlation and making an elevation line plot.
"""

# %%
# 1. Import cf-python, cf-plot and other required packages:
import cfplot as cfp
import cf

import matplotlib.pyplot as plt
import scipy.stats.mstats as mstats

# %%
# 2. Read the data in:
# We are investigating the influence of the land height on the snow cover,
# so snow cover is the dependent variable. You can use different variable
# names for easier understanding.
# We are selecting the first field in the data with [0]
PATH = "~/summerstudents/final-recipes/new-required-datasets"
orog = cf.read(f"{PATH}/1km_elevation.nc")[0]
snow = cf.read(f"{PATH}/snowcover")[0]
# Could use any of the seven days by indexing differently
snow_day = snow[0]  # first day, Jan 1st of this year (2024)

# %%
# 3. Choose the regions and subspace to same area for both datasets:
# Ensuring both datasets cover it, and also that its not too large as then
# regridding could cause the program to crash on small computers (dont
# regrid the whole map), as well as being mainly land.
# Tool for finding rectangular  area for lat and lon points
# https://www.findlatitudeandlongitude.com/l/Yorkshire%2C+England/5009414/
region_in_mid_uk = [(-3.0, -1.0), (52.0, 55.0)]  # lon then lat
sub_orog = orog.subspace(
    longitude=cf.wi(*region_in_mid_uk[0]), latitude=cf.wi(*region_in_mid_uk[1])
)
sub_snow = snow_day.subspace(
    longitude=cf.wi(*region_in_mid_uk[0]), latitude=cf.wi(*region_in_mid_uk[1])
)

# %%
# 4. Normalise the data and change the units appropriately.
# Reassign the units as they are removed by cf-python after calculation
# Only do this if you are certain the units are convertible to %
# This normalises to between 0 and 1 so multiply by 100 to get a percentage:
sub_snow = ((sub_snow - sub_snow.minimum()) / (sub_snow.range())) * 100
sub_snow.override_units("1", inplace=True)

# %%
# 5. Regrid the data to have a comparable array.
# Here the orography file is regridded to the snow file
# as snow is higher resolution (if this doesnt work switch them).
regridded_orog = sub_orog.regrids(sub_snow, method="linear")

# %%
# 6. Squeeze snow data to remove the size 1 axes
sub_snow = sub_snow.squeeze()

# %%
#  7. Final statistical calculations
coefficient = mstats.pearsonr(regridded_orog.array, sub_snow.array)
print(f"The Pearson correlation coefficient is: {coefficient}")


# %%
# 8. Plots including title stating the coefficient.
# First it outputs the newly formatted data, you can change the file names
# the plots will save as.
# colour_scale.txt is a colour scale specifically made and saved to show
# the data but you could make your own or use existing ones from
# https://ncas-cms.github.io/cf-plot/build/colour_scales.html
# You will also need to adjust the labels and axis for your regridded_orogion
cfp.gopen(
    rows=1, columns=2, top=0.85,
    file="snow_and_orog_on_same_grid.png",
    user_position=True,
)

# Joint config including adding an overall title
plt.suptitle(
    (
        "Snow cover compared to elevation for the same area of the UK "
        "at midnight\n2024-01-01, with correlation coefficient "
        f"(on the same grid) of {coefficient.statistic:.4g} (4 s.f.)"
    ),
    fontsize=17,
)
cfp.mapset(resolution="10m")
cfp.setvars(ocean_color="white", lake_color="white")
label_info = {
    "xticklabels": ("3W", "2W", "1W"),
    "yticklabels": ("52N", "53N", "54N", "55N"),
    "xticks": (-3, -2, -1),
    "yticks": (52, 53, 54, 55),
}

# PLot the two contour plots as columns
cfp.gpos(1)
cfp.cscale("wiki_2_0_reduced")
cfp.con(
    regridded_orog,
    lines=False,
    title="Elevation (from 1km-resolution orography)",
    colorbar_drawedges=False,
    **label_info,
)
cfp.gpos(2)
cfp.cscale("precip4_11lev", ncols=22, reverse=1)
cfp.con(sub_snow, lines=False,
        title="Snow cover extent (from satellite imagery)",
        colorbar_drawedges=False,
        **label_info
)

cfp.gclose()
