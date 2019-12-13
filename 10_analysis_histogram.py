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
import re


def getCmdArgs():
    '''
    Get commdnaline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Combines voxel PAI estimates from multiple scans"))
    p.add_argument("inputData",
                   type=str, help=("Input of combined scans [No default]"))
    p.add_argument("-H", "--histogram", dest="histogram", default="histogram.png",
                   type=str, help=("Output histogram plot image\n[histogram.png]"))
    p.add_argument("-x", "--x-var", dest="xVar", default="mGapTo",
                   type=str, help=("Name of the x variable\n[mGapTo]"))
    p.add_argument("-y", "--y-var", dest="yVar", default="mPAIb_mGapTo",
                   type=str, help=("Name of the x variable\n[mPAIb_mGapTo]"))
    p.add_argument("-n", "--n-bins", dest="nBins", default=100,
                   type=int, help=("Number of bins to aggregate x data\n[100]"))
    p.add_argument("-d", "--max-y-difference", dest="maxDifference", default=20.0,
                   type=float, help=("Maximum y absolute difference\n[20]"))
    p.add_argument("-v", "--vox-resolution", dest="resolution", default=0.5,
                   type=float, help=("Voxel resolution\n[0.5]"))
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

def plotHistogram(outputPath, xVec, yVec, xVar):
    # Plot mean + error
    rebinned = np.round(xVec / 5).astype(np.int)
    uniques = np.unique(rebinned)
    for i in uniques:
        maskVal = rebinned == i
        name = str(i*5)
        ax = fig()
        hist = np.histogram(yVec[maskVal], bins=1000)
        secondLargest = np.partition(hist[0], -2)[-2]
        sns.distplot(yVec[maskVal], bins=1000, kde=False, norm_hist=False)
        plt.xlim(np.quantile(yVec[maskVal], 0.001), np.quantile(yVec[maskVal], 0.999))
        plt.ylim(0, secondLargest*1.2)
        plt.xlabel(r"Diff LAIv")
        plt.ylabel(r"Frequency")
        output = re.sub(r"\.[^\.]*$", name + ".png", outputPath)
        plt.savefig(output)
        plt.close()


if __name__ == "__main__":    
    args = getCmdArgs()
    yVar2 = "v2_" + args.yVar

    data = openData(args.inputData)
    yDiff = calculateDiff(data, args.yVar, yVar2) * args.resolution

    mask = getMaskNoData(data, args.yVar, yVar2, args.xVar)
    mask = mask & (np.abs(yDiff) <= args.maxDifference)

    aggregatedX = aggregateX(data[args.xVar], data["v2_" + args.xVar])
    normalizedX = normalizeXVar(aggregatedX, args.nBins)

    plotHistogram(args.histogram, normalizedX[mask], yDiff[mask], args.xVar)
