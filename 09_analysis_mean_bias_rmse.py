# %%
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import ndimage
import argparse


def getCmdArgs():
    '''
    Get commdnaline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Combines voxel PAI estimates from multiple scans"))
    p.add_argument("inputData",
                   type=str, help=("Input of combined scans [No default]"))
    p.add_argument("-m", "--mean-plot", dest="meanPlot", default="mean_plot.png",
                   type=str, help=("Output mean bias plot image\n[mean_plot.png]"))
    p.add_argument("-r", "--rmse-plot", dest="rmsePlot", default="rmse_plot.png",
                   type=str, help=("Output RMSE plot image\n[rmse_plot.png]"))
    p.add_argument("-x", "--x-var", dest="xVar", default="mGapTo",
                   type=str, help=("Name of the x variable\n[mGapTo]"))
    p.add_argument("-y", "--y-var", dest="yVar", default="mPAIb_mGapTo",
                   type=str, help=("Name of the x variable\n[mPAIb_mGapTo]"))
    p.add_argument("-n", "--n-bins", dest="nBins", default=100,
                   type=int, help=("Number of bins to aggregate x data\n[100]"))
    p.add_argument("-d", "--max-y-difference", dest="maxDifference", default=20.0,
                   type=float, help=("Maximum y absolute difference\n[20]"))
    cmdargs = p.parse_args()
    return cmdargs


# %% Funcs
def fig():
    my_dpi = 96
    fig, ax = plt.subplots()
    fig.set_size_inches(1920/my_dpi, 1080/my_dpi)
    fig.set_dpi(my_dpi)
    return ax

def openData(inputPath):
    data = pd.read_csv(inputPath, sep=" ")
    return data

def calculateDiff(data, yVar, yVar2):
    return data[yVar2]-data[yVar]

def getMaskNoData(data, yVar, yVar2, xVar):
    return (data[yVar] >= 0) & (data[yVar2] >= 0) & (
        data[xVar] >= 0)

def normalizeXVar(xVec, nBins):
    minVal = xVec.min()
    maxVal = np.quantile(xVec, 1)
    normalized = np.floor(
        nBins*(xVec-minVal)/(maxVal-minVal)).astype(np.uint)
    normalized[xVec > maxVal] = nBins
    return normalized

def aggregateX(xVec1, xVec2):
    return np.min(np.stack([xVec1, xVec2]), axis=0)

def plotMeanBias(outputPath, xVec, yVec, xVar):
    # Plot mean + error
    ax = fig()
    ax.axhline(y=0, linewidth=1, color="black", linestyle="--")
    sns.lineplot(x=xVec, y=yVec, ax=ax)
    plt.ylabel(r"$\mu$ LADv difference")
    plt.xlabel(xVar)
    plt.savefig(outputPath)
    plt.close()

def plotRMSE(outputPath, xVec, yVec, xVar):
    # Plot std
    ax = fig()
    uniques = np.unique(xVec)
    rmse = ndimage.standard_deviation(yVec, xVec, uniques)
    sns.lineplot(x=uniques, y=rmse, ax=ax)
    plt.ylabel(r"RMSE LADv difference")
    plt.xlabel(xVar)
    plt.savefig(outputPath)
    plt.close()

if __name__ == "__main__":    
    args = getCmdArgs()
    yVar2 = "v2_" + args.yVar

    data = openData(args.inputData)
    yDiff = calculateDiff(data, args.yVar, yVar2)

    mask = getMaskNoData(data, args.yVar, yVar2, args.xVar)
    mask = mask & (np.abs(yDiff) <= args.maxDifference)

    aggregatedX = aggregateX(data[args.xVar], data["v2_" + args.xVar])
    normalizedX = normalizeXVar(aggregatedX, args.nBins)

    plotMeanBias(args.meanPlot, normalizedX[mask], yDiff[mask], args.xVar)
    plotRMSE(args.rmsePlot, normalizedX[mask], yDiff[mask], args.xVar)
