from glob import glob
import os
from pathlib import Path
import re
import pandas as pd

# Recursively look for matching transform matrices and rxp scans for each year
y = '2018'

# Read point clouds and transform matrices path for specified year as pandas series
scans = pd.Series(glob('../riegl/' + y + '/**/SINGLESCANS/*.rxp', recursive=True))
transforms = pd.Series(glob('../riegl/' + y + '/**/*.DAT', recursive=True))

# Extract plot and scan information for transform and point clouds
transform_plot = transforms.str.extract("(Plot_\d+)")
transforms_without_spaces = transforms.str.replace(" ", "")
transform_raw_names = transforms_without_spaces.str.extract("/([^/]*)\.DAT$")
scans_folder_name = scans.str.extract("/([^/]*)/SINGLESCANS")[0].str.replace(" ", "")
scans_plot_name = scans.str.extract("(Plot_\d+)")

# Build DataFrames
transform_df = pd.DataFrame({"plot": transform_plot[0], "scan": transform_raw_names[0], "transform_matrix": transforms})
scans_df = pd.DataFrame({"plot":scans_plot_name[0], "scan":scans_folder_name, "point_cloud":scans})

# Group by plot and scan taking first for transform (transform files are repeated)
transform_df = transform_df.groupby(["plot", "scan"])["transform_matrix"].first().reset_index()

# Group by plot and scan making a list of point cloud rxp files
grouped_by_folder_plot = scans_df.groupby(["plot", "scan"])["point_cloud"].apply(list).reset_index()
grouped_by_folder_plot["n_point_clouds"] = grouped_by_folder_plot["point_cloud"].apply(len)

# Join transform and scans to know which transform matrix to apply to each scan
result = pd.merge(transform_df, grouped_by_folder_plot, how="inner", left_on=["plot","scan"], right_on=["plot","scan"])
result.to_csv("scans.csv", index=False)
