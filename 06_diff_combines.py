#!/usr/bin/env python3

import pandas as pd
import os
import sys
from sklearn.neighbors import NearestNeighbors


def parse_error(error):
    sys.stderr.write(
        "{}!\nUsage: 'python3 {} <first_file> <second_file>'\n".format(
            error, sys.argv[0]
        ))
    sys.exit(-1)


def input_args_checking(n_args):
    if (len(sys.argv) != n_args+1):
        parse_error("Wrong number of inputs")

    if (not os.path.isfile(sys.argv[1])):
        parse_error("First file is not a file")
    if (not os.path.isfile(sys.argv[2])):
        parse_error("Second file is not a file")


if __name__ == "__main__":
    input_args_checking(2)

    first = sys.argv[1]
    second = sys.argv[2]
    spatial_columns = ["x",  "y",  "z"]
    colNames = [
        "x",  "y",  "z",  "mGapTo",  "maxGapTo",  "mGapIn",
        "mPAIb_mGapTo",  "mPAIrad",  "totBeam",  "bPAIb", "maxVol",
        "volTrans", "mPAIb_volTrans", "mPAIb_totBeam"]
    data = pd.read_csv(first, sep=" ", skiprows=[0], names=colNames)
    data2 = pd.read_csv(second, sep=" ", skiprows=[0], names=colNames)

    nbrs = NearestNeighbors(
        n_neighbors=2,
        algorithm='kd_tree').fit(data2[spatial_columns])
    (dist, nn) = nbrs.kneighbors(data[spatial_columns], 1)

    final = data[:]

    vals = data2.iloc[nn.flatten(), 3:]
    vals_diff = vals.reset_index().iloc[:, 1:]
    vals_diff.columns = "v2_" + vals_diff.columns

    final = data.join(vals_diff)
    final["dist"] = dist

    first_base = os.path.splitext(os.path.basename(first))[0]
    second_base = os.path.splitext(os.path.basename(second))[0]

    dir_name = os.path.dirname(first)
    out_file_name = "{}/diff_{}-{}".format(dir_name, first_base, second_base)
    final.to_csv(out_file_name, sep=" ", index=False)
    print("Done writing {}".format(os.path.basename(out_file_name)))
