#!/usr/bin/env python3

from multiprocessing import Pool
from glob import glob
import pandas as pd
import os
import sys
import subprocess

   

def do_work(cmd):
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    sys.stdout.flush()


def parse_error(error):
    sys.stderr.write("{}!\nUsage: 'python3 {} <input_path> <output_path> <csv_file> <resolution> <n_cores>'\n".format(error, sys.argv[0]))
    sys.exit(-1)

def input_args_checking_return_cores(n_args):
    n = 1

    if (len(sys.argv) != n_args+1):
        parse_error("Wrong number of inputs")

    try:
        n = int(sys.argv[n_args])
    except:
        parse_error("Number of cores is not a number")

    if (not os.path.isdir(sys.argv[1])):
        parse_error("Input path is not a valid path")
    if (not os.path.isdir(sys.argv[2])):
        parse_error("Output path is not a valid path")
    if (not os.path.isfile(sys.argv[3])):
        parse_error("CSV path is not a valid")

    return n


if __name__ == '__main__':
    n_args = 5

    n_cores = input_args_checking_return_cores(n_args)

    in_path = sys.argv[1]
    out_path = sys.argv[2]
    csv_file = sys.argv[3]
    res = sys.argv[4]

    # Start the pool
    pool = Pool(n_cores)

    # Grab files and build input and output absolute paths
    files = glob(os.path.join(in_path, '*.bin'))
    files_df = pd.DataFrame({"input": files})
    files_df["filename"] = files_df.iloc[:,0].str.extract(r"([^/\\]*)\.bin")
    files_df["output"] = os.path.normpath(out_path) + "/" + files_df["filename"] + ".txt"

    # Grab the transform CSV matrix
    df = pd.read_csv(csv_file)
    df["new_filename"] = df["plot"] + "_" + df["scan"] + "_" + df["point_cloud"].str.extract(r"([^/\\]*)\.rxp")[0]
    files_df = files_df.merge(df, left_on="filename", right_on="new_filename")

    # Main loop 
    columns = ['input', 'output', 'transform_matrix']
    cmds = []
    ground_offset = 20
    offset = 20
    tree_max_height = 40
    for (i, f) in files_df[columns].iterrows():
        (infile, outfile, transform) = f
        # Get x, y, and z offset from transformation matrix
        transform_matrix_df = pd.read_csv(transform, sep=" ", header=None)
        (x, y, z) = transform_matrix_df.iloc[:3,3]

        # Set offsets to build up the boundaries to use for voxelTLS
        xmin = -offset
        xmax = offset
        ymin = -offset
        ymax = offset
        zmin = z - ground_offset
        zmax = z + ground_offset + tree_max_height
        # Build the command
        cmd = 'voxelTLS -input "{}" -res {} -bounds {} {} {} {} {} {} -voxGap -output "{}"'.format(infile, res, xmin, ymin, zmin, xmax, ymax, zmax, outfile)    
        cmds.append(cmd)
    # Run the commands in parallel
    pool.map(do_work, cmds)
