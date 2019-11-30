#!/usr/bin/env python3

import numpy as np
import pandas as pd
import argparse
from sys import exit


###############################
# Combines output of voxelTLS #
# from multiple scans         #
#                             #
# svenhancock@gmail.com       #
# November 2018               #
###############################

# CONSTANTS
COLS_DICT = {
    1: "x",
    2: "y",
    3: "z",
    4: "gap0",
    5: "inHit0",
    6: "inMiss0",
    7: "gapTo0",
    8: "hits0",
    9: "miss0",
    10: "PAIbel0",
    11: "volSamp0",
    12: "volTrans0",
    13: "PAIrad0",
    14: "meanRefl0",
    15: "meanZen0"
}
COLS_SEL = {
    "x": "x",
    "y": "y",
    "z": "z",
    "gap0": "gapIn",
    "gapTo0": "gapTo",
    "hits0": "nBeam",
    "PAIbel0": "PAIb",
    "PAIrad0": "PAIrad",
    "volSamp0": "volSamp",
    "volTrans0": "volTrans"
}
USECOLS = {key: COLS_SEL[value] for (key, value) in COLS_DICT.items()
           if value in COLS_SEL.keys()}
USECOLS_NAMES = list(USECOLS.values())
COLS_IND = {USECOLS_NAMES[i]: i-3 for i in range(3, len(USECOLS))}
COLS_IND_ARR = np.array(list(USECOLS.items()))
COLS_IND_ARR[:, 0] = COLS_IND_ARR[:, 0].astype(np.int) - 1

##############################################
# read the command line
##############################################


def getCmdArgs():
    '''
    Get commdnaline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Combines voxel PAI estimates from multiple scans"))
    p.add_argument("--input", dest="inNamen", default=" ",
                   type=str, help=("Input of combined scans\nNo default"))
    p.add_argument("--inList", dest="listNamen", default=" ",
                   type=str, help=("Input list of single scans\nNo default"))
    p.add_argument("--output", dest="outNamen", default="meanVox.vox",
                   type=str, help=("Outpt filename\nDefault = meanVox.vox"))
    p.add_argument("--minGap", dest="minGap", type=float, default=0.0,
                   help=("Minimum trustable gap fraction to a voxel\n\
                       Default = 0"))
    cmdargs = p.parse_args()
    return cmdargs


def readData(inName, listName):
    '''Read the data'''
    # do we have a single file
    if(inName != " "):
        return readScan(inName, position=True)
    elif(listName != " "):   # multiple files
        return readMultipleScans(listName)
    else:   # no input. Fail program
        print("No input specified")
        exit(1)


def readScan(inName, position=False):
    cols = COLS_IND_ARR[:, 1]
    usecols = COLS_IND_ARR[:, 0].astype(np.int)
    if position is False:
        cols = cols[3:]
        usecols = usecols[3:]
    data = pd.read_csv(inName, skiprows=1,
                       sep=" ", names=cols, usecols=usecols)

    if position is True:
        pos = data.iloc[:, :3]
        data = data.iloc[:, 3:]
        return (pos, np.dstack([data.to_numpy()]))
    else:
        return np.dstack([data.to_numpy()])


def readMultipleScans(listName):
    files = np.loadtxt(listName, unpack=True, usecols=(
        0,), dtype=str, comments='#', delimiter=" ")
    nScans = len(files)
    i = 0
    pos = 0
    arrays_list = []
    for file in files:
        print("\rReading scan: {}/{}       ".format(i + 1, nScans), end="")
        if i == 0:
            pos, data = readScan(file, position=True)
        else:
            data = readScan(file, position=False)

        arrays_list.append(data)
        i += 1

    return (pos, np.dstack(arrays_list))

def mask_by(data, var, minGap):
    # Create a mask based on gapTo minGap
    mask = data[:, COLS_IND[var], :] < minGap
    # Axis 0 == voxel
    # Axis 1 == variables (columns)
    # Axis 2 == scan
    mask = np.expand_dims(mask, axis=1)  # Add axis corresponding to vars
    mask = np.repeat(mask, data.shape[1], axis=1)  # Repeat mask for all vars
    return np.ma.masked_array(data, mask)

def combineData(pos, data, minGap):
    result = pos

    data_mask = mask_by(data, "gapTo", minGap)

    gapTo = data_mask[:, COLS_IND["gapTo"], :]  # Alias for gapTo var
    result["4_mGapTo"] = np.average(
        gapTo, weights=gapTo, axis=1).filled(-1)
    result["5_maxGapTo"] = np.max(gapTo, axis=1).filled(-1)
    result["6_mGapIn"] = np.average(
        data_mask[:, COLS_IND["gapIn"], :], weights=gapTo, axis=1).filled(-1)
    result["7_mPAIb"] = np.average(
        data_mask[:, COLS_IND["PAIb"], :], weights=gapTo, axis=1).filled(-1)
    result["8_mPAIrad"] = np.average(
        data_mask[:, COLS_IND["PAIrad"], :], weights=gapTo, axis=1).filled(-1)
    result["9_totBeam"] = np.sum(
        data_mask[:, COLS_IND["nBeam"], :], axis=1).filled(0).astype(np.uint32)

    # fit a function for waveform based PAI
    # gapTo[i,useInd],meanRefl[i,useInd],meanZen[i,useInd])
    # mPAIw = self.fitLAD(i, useInd)
    # Beland's maximum visibility PAI
    gap_to_max_ind = np.argmax(gapTo, axis=1)
    row_sequence = np.arange(data_mask.shape[0])
    result["10_bPAIb"] = data_mask[row_sequence,
                                   COLS_IND["PAIb"], gap_to_max_ind].filled(-1)
    result["11_maxVol"] = \
        data_mask[row_sequence, COLS_IND["volSamp"], gap_to_max_ind]\
        / \
        data_mask[row_sequence, COLS_IND["volTrans"], gap_to_max_ind]
    result["12_maxVolTrans"] = np.max(data_mask[:, COLS_IND["volTrans"], :], axis=1).filled(-1)
    
    data_mask = mask_by(data, "volTrans", minGap)
    result["13_mPAIb_volTrans"] = np.average(
        data_mask[:, COLS_IND["PAIb"], :],
        weights=data_mask[:, COLS_IND["volTrans"], :],
        axis=1).filled(-1)
    data_mask = mask_by(data, "nBeam", minGap)
    result["14_mPAIb_nBeams"] = np.average(
        data_mask[:, COLS_IND["PAIb"], :],
        weights=data_mask[:, COLS_IND["nBeam"], :],
        axis=1).filled(-1)
    return result


##############################################
# main
##############################################
if __name__ == '__main__':
    # read command line
    cmdargs = getCmdArgs()
    # transfer to local variables, to ease debugging
    inNamen = cmdargs.inNamen
    listNamen = cmdargs.listNamen
    minGap = cmdargs.minGap
    outNamen = cmdargs.outNamen

    # read data
    pos, data = readData(inNamen, listNamen)

    # combine data
    print("\nProcessing data...", end="")
    result = combineData(pos, data, minGap)

    # write csv
    print("\rWriting output...", end="")
    result.to_csv(outNamen, sep=" ", header=True, index=False)
    print(" Finished!")


##############################################
# end
##############################################
# inNamen = " "
# listNamen = "d1l1.txt"
# minGap = 0.01
# outNamen="out.txt"
