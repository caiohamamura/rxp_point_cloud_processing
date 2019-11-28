# %%
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

# %% Constants
nBins = 100
vars = ["mGapTo", "totBeam", "volSamp"]
voxelRes = 0.75


# %% Funcs
def fig():
    my_dpi = 96
    fig, ax = plt.subplots()
    fig.set_size_inches(1920/my_dpi, 1080/my_dpi)
    fig.set_dpi(my_dpi)
    return ax


# %%
os.chdir("Z:/python/results")
data = pd.read_csv("diff_d1l1.csv-d1l2.csv", sep=" ")
append = "_locs"
data.head()

# %%
for var in vars:
    mask = (data["mPAIb"] >= 0) & (data["v2_mPAIb"] >= 0) & (
        data[var] >= 0) & (data[var] >= 0)
    data["diff_mPAIb"] = data["v2_mPAIb"]-data["mPAIb"]
    mask = mask & (data["diff_mPAIb"].abs() <= 25)

    # Divide in multiple bins
    varLevel = var + "Level"
    minVal = data[var].min()
    maxVal = data[var].quantile(0.98)
    data[varLevel] = np.floor(
        nBins*(data[var]-minVal)/(maxVal-minVal)).astype(np.uint)

    data.loc[data[var] > maxVal, varLevel] = nBins

    # Plot mean + error
    ax = fig()
    ax.axhline(y=0, linewidth=1, color="black", linestyle="--")
    data["diff_LA"] = data["diff_mPAIb"]*(voxelRes**3 * 30)
    sns.lineplot(x=varLevel, y="diff_LA", data=data[mask], ax=ax)
    plt.ylabel(r"$\mu$ LA difference")
    plt.xlabel(var)
    plt.savefig("T:/Win7/Desktop/mean_bias" + append + "_" + var + ".png")
    plt.close()

    # Plot std
    ax = fig()
    res = data[mask].groupby(varLevel)["diff_LA"].std().reset_index()
    sns.lineplot(x=varLevel, y="diff_LA", data=res, ax=ax)
    plt.ylabel(r"RMSE LA difference")
    plt.xlabel(var)
    plt.savefig("T:/Win7/Desktop/std_bias" + append + "_" + var + ".png")
    plt.close()

    # #Histogram
    # ax = fig()
    # res=data[mask].groupby(varLevel)["diff_mPAIb"].count()
    # sns.lineplot(x=varLevel, y="diff_mPAIb", data=data[mask], ax=ax)
    # plt.ylabel(r"$\sigma$ mPAIb difference")
    # plt.xlabel(var + r" (%)")
    # plt.savefig("T:/Win7/Desktop/std_bias" + append + "_" + var + ".png")
    # plt.close()


# %%
#Histogram
sns.distplot(data["diff_mPAIb"])
plt.xlim((-1,1))
plt.xlabel(r"Diff mPAIb")


# %%
var = "mGapTo"
var = "mGapTo"
data["diff_LA"] = data["diff_mPAIb"]*(voxelRes**3 * 30)
data["diff_bLA"] = data["diff_bPAIb"]*(voxelRes**3 * 30)
# Divide in multiple bins
varLevel = var + "Level"
minVal = data[var].min()
maxVal = data[var].quantile(0.98)
data[varLevel] = np.floor(
    nBins*(data[var]-minVal)/(maxVal-minVal)).astype(np.uint)

data.loc[data[var] > maxVal, varLevel] = nBins
mask = data[varLevel] == 70
sns.distplot(data[mask]["diff_LA"], bins=100)
sns.distplot(data[mask]["diff_bLA"], bins=100)
plt.xlim(-25, 25)

# %%
var = "mGapTo"
var2 = "v2_mGapTo"
data["diff_bPAIb"] = data["v2_mPAIb"]-data["mPAIb"]
data["diff_LA"] = data["diff_mPAIb"]*(voxelRes**3 * 30)
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

mask = (data[varLevel] >= 70) & (data[varLevel2] >= 70) & (abs(data["diff_LA"]) > 8) & (data["mGapIn"] >= 0) & (data["v2_mGapIn"] >= 0)
data[mask].to_csv("R:/masked_diff_LA.pts", sep=" ", index=False)

# %%
data[["x", "y", "z", "diff_LA"]].to_csv("R:/full_diff_LA.pts", sep=" ")

# %%
