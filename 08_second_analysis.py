# %%
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

# %% Funcs
def fig():
    my_dpi = 96
    fig, ax = plt.subplots()
    fig.set_size_inches(1920/my_dpi, 1080/my_dpi)
    fig.set_dpi(my_dpi)
    return ax

# %% Constants
nBins = 100
var "mGapTo"
voxelRess = np.array([0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
yVar = "mPAIb"


# %%
os.chdir("Z:/python/multi_voxel")
append = "d1locs"

# %%
for voxelRes in voxelRess:
    data = pd.read_csv("diff_d1l1_{0}.csv-d1l2_{0}.csv".format(voxelRes), sep=" ")
    yVarLocal = yVar + "_" + var
    v2_yVarLocal = "v2_" + yVarLocal
    diffVar = "diff_" + yVarLocal
    diffLA = "diff_LA_" + var
    var2 = "v2_" + var
    xVar = "min_" + var
    data[xVar] = data[[var, var2]].min(axis=1)

    mask = (data[yVarLocal] >= 0) & (data[v2_yVarLocal] >= 0) & (
        data[xVar] >= 0)
    data[diffVar] = data[v2_yVarLocal]-data[yVarLocal]
    mask = mask & (data[diffVar].abs() <= 25)

    # Divide in multiple bins
    varLevel = var + "Level"
    minVal = data[xVar].min()
    maxVal = data[xVar].quantile(0.98)
    data[varLevel] = np.floor(
        nBins*(data[xVar]-minVal)/(maxVal-minVal)).astype(np.uint)

    data.loc[data[xVar] > maxVal, varLevel] = nBins

    # Plot mean + error
    ax = fig()
    ax.axhline(y=0, linewidth=1, color="black", linestyle="--")
    data[diffLA] = data[diffVar]*(voxelRes**3 * 30)
    sns.lineplot(x=varLevel, y=diffLA, data=data[mask], ax=ax)
    plt.ylabel(r"$\mu$ LA difference avg by " + var)
    plt.xlabel(xVar)
    plt.savefig("T:/Win7/Desktop/res-{}_{}_x-{}_y-{}_mean.png".format(voxelRes, append, xVar, diffLA))
    plt.close()

    # Plot std
    ax = fig()
    res = data[mask].groupby(varLevel)[diffLA].std().reset_index()
    sns.lineplot(x=varLevel, y=diffLA, data=res, ax=ax)
    plt.ylabel(r"RMSE LA difference avg by " + var)
    plt.xlabel(xVar)
    plt.savefig("T:/Win7/Desktop/res-{}_{}_x-{}_y-{}_rmse.png".format(voxelRes, append, xVar, diffLA))
    plt.close()

    for var in vars:
        if var == "mGapTo":
            continue

        yVarLocal = yVar + "_" + var
        v2_yVarLocal = "v2_" + yVarLocal
        diffVar = "diff_" + yVarLocal
        diffLA = "diff_LA_" + var
        varX = "mGapTo"
        var2 = "v2_" + varX
        xVar = "min_" + varX
        data[xVar] = data[[varX, var2]].min(axis=1)

        mask = (data[yVarLocal] >= 0) & (data[v2_yVarLocal] >= 0) & (
            data[xVar] >= 0)
        data[diffVar] = data[v2_yVarLocal]-data[yVarLocal]
        mask = mask & (data[diffVar].abs() <= 25)

        # Divide in multiple bins
        varLevel = var + "Level"
        minVal = data[xVar].min()
        maxVal = data[xVar].quantile(0.98)
        data[varLevel] = np.floor(
            nBins*(data[xVar]-minVal)/(maxVal-minVal)).astype(np.uint)

        data.loc[data[xVar] > maxVal, varLevel] = nBins

        # Plot mean + error
        ax = fig()
        ax.axhline(y=0, linewidth=1, color="black", linestyle="--")
        data[diffLA] = data[diffVar]*(voxelRes**3 * 30)
        sns.lineplot(x=varLevel, y=diffLA, data=data[mask], ax=ax)
        plt.ylabel(r"$\mu$ LA difference avg by " + var)
        plt.xlabel(xVar)
        plt.savefig("T:/Win7/Desktop/res-{}_{}_x-{}_y-{}_mean.png".format(voxelRes, append, xVar, diffLA))
        plt.close()

        # Plot std
        ax = fig()
        res = data[mask].groupby(varLevel)[diffLA].std().reset_index()
        sns.lineplot(x=varLevel, y=diffLA, data=res, ax=ax)
        plt.ylabel(r"RMSE LA difference avg by " + var)
        plt.xlabel(xVar)
        plt.savefig("T:/Win7/Desktop/res-{}_{}_x-{}_y-{}_rmse.png".format(voxelRes, append, xVar, diffLA))
        plt.close()


# %%
#Histogram
sns.distplot(data[diffVar])
plt.xlim((-1,1))
plt.xlabel(r"Diff mPAIb")


# %%
var = "mGapTo"
var = "mGapTo"
data[diffLA] = data[diffVar]*(voxelRes**3 * 30)
data["diff_bLA"] = data["diff_bPAIb"]*(voxelRes**3 * 30)
# Divide in multiple bins
varLevel = var + "Level"
minVal = data[var].min()
maxVal = data[var].quantile(0.98)
data[varLevel] = np.floor(
    nBins*(data[var]-minVal)/(maxVal-minVal)).astype(np.uint)

data.loc[data[var] > maxVal, varLevel] = nBins
mask = data[varLevel] == 70
sns.distplot(data[mask][diffLA], bins=100)
sns.distplot(data[mask]["diff_bLA"], bins=100)
plt.xlim(-25, 25)

# %%
var = "mGapTo"
var2 = "v2_mGapTo"
data["diff_bPAIb"] = data[v2_yVarLocal]-data[yVarLocal]
data[diffLA] = data[diffVar]*(voxelRes**3 * 30)
# Divide in multiple bins
varLevel = var + "Level"
minVal = data[var].min()
maxVal = data[var].quantile(0.98)
data[varLevel] = np.floor(
    nBins*(data[var]-minVal)/(maxVal-minVal)).astype(np.uint)
data.loc[data[var] > maxVal, varLevel] = nBins

varLevel2 = var2 + "Level" 
minVal = data[var2].min()
maxVal = data[var2].quantile(0.98)
data[varLevel2] = np.floor(
    nBins*(data[var2]-minVal)/(maxVal-minVal)).astype(np.uint)
data.loc[data[var2] > maxVal, varLevel2] = nBins

mask = (data[varLevel] >= 70) & (data[varLevel2] >= 70) & (abs(data[diffLA]) > 8) & (data["mGapIn"] >= 0) & (data["v2_mGapIn"] >= 0)
data[mask].to_csv("R:/masked_diff_LA.pts", sep=" ", index=False)

# %%
data[["x", "y", "z", diffLA]].to_csv("R:/full_diff_LA.pts", sep=" ")

# %%


%%
