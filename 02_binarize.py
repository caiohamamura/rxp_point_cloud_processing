#!/usr/bin/env python3

from multiprocessing import Pool
import pandas as pd
import os
import sys



def f(cmd):
    print(os.popen(cmd).read())


def parse_error(error):
    sys.stderr.write("{}!\nUsage: 'python3 {} <number_of_cores> <output_path> <csv_file>'\n".format(error, sys.argv[0]))
    sys.exit(-1)


if __name__ == '__main__':
    n = 4

    if (len(sys.argv) != n):
        parse_error("Wrong number of inputs")

    try:
        n = int(sys.argv[1])
    except:
        parse_error("Number of cores is not a number")

    if (not os.path.isdir(sys.argv[2])):
        parse_error("Output path is not a valid path")

    out_path = sys.argv[2]
    csv_file = sys.argv[3]

    pool = Pool(n)
    df = pd.read_csv(csv_file)
    target_cols = df[["plot", "scan", "transform_matrix", "point_cloud"]]
    cmds = []
    for (i, (plot, scan, t, pc)) in target_cols.iterrows():
        basename = os.path.basename(pc)[:-4]
        cmd = 'readRXP -input "{}"  -trans "{}" -output "{}/{}_{}_{}.bin"'.format(pc, t, out_path, plot, scan, basename)    
        cmds.append(cmd)
    pool.map(f, cmds)
    
