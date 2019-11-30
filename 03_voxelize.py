#!/usr/bin/env python3

from multiprocessing import Pool
from glob import glob
import pandas as pd
import os
import sys
import argparse
import subprocess


def getCmdArgs():
    '''
    Get commdnaline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Combines voxel PAI estimates from multiple scans"))
    p.add_argument("input_path",
                   type=str,
                   help="Input path for where binary clouds are")

    p.add_argument("output_path",
                   type=str,
                   help="Output path")

    p.add_argument("csv_file",
                   type=str,
                   help="CSV relatioship files")

    p.add_argument("resolution",
                   type=float,
                   help="Resolution for voxels")

    p.add_argument("-j", "--jobs",
                   dest="threads",
                   type=int,
                   default=os.cpu_count()-1,
                   help="Number of cores")

    p.add_argument("-z", "--z_min",
                   dest="z_min",
                   type=float,
                   default=-9999,
                   help="Minimum Z value")

    p.add_argument("-Z", "--z_max",
                   dest="z_max",
                   type=float,
                   default=-9999,
                   help="Maximum Z value")
    return p


def do_work(cmd):
    subprocess.check_call(cmd, shell=True,
                          stdout=sys.stdout,
                          stderr=subprocess.STDOUT)
    sys.stdout.flush()


def parse_error(parse, error):
    print(error, file=sys.stderr)
    parse.print_help(sys.stderr)
    sys.exit(-1)


def input_args_checking_return_cores(parse, args):
    if (not os.path.isdir(args.input_path)):
        parse_error(parse, "Input path is not a valid path")

    if (not os.path.isdir(args.output_path)):
        parse_error(parse, "Output path is not a valid path")

    if (not os.path.isfile(args.csv_file)):
        parse_error(parse, "CSV path is not a valid")


if __name__ == '__main__':
    parse = getCmdArgs()
    args = parse.parse_args()
    n_cores = args.threads

    input_args_checking_return_cores(parse, args)

    in_path = args.input_path
    out_path = args.output_path
    csv_file = args.csv_file
    res = args.resolution

    # Start the pool
    pool = Pool(n_cores)

    # Grab files and build input and output absolute paths
    files = glob(os.path.join(in_path, '*.bin'))
    files_df = pd.DataFrame({"input": files})
    files_df["filename"] = files_df.iloc[:, 0].str.extract(r"([^/\\]*)\.bin")
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
        if (args.z_min == -9999 or args.z_max == -9999):
            transform_matrix_df = pd.read_csv(transform, sep=" ", header=None)
            (x, y, z) = transform_matrix_df.iloc[:3, 3]
            zmin = z - ground_offset
            zmax = z + ground_offset + tree_max_height
        else:
            zmin = args.z_min
            zmax = args.z_max

        # Set offsets to build up the boundaries to use for voxelTLS
        xmin = -offset
        xmax = offset
        ymin = -offset
        ymax = offset
        
        # Build the command
        cmd = 'voxelTLS -input "{}" -res {} -bounds {} {} {} {} {} {} -voxGap -output "{}"'.format(infile, res, xmin, ymin, zmin, xmax, ymax, zmax, outfile)
        cmds.append(cmd)
    # Run the commands in parallel
    pool.map(do_work, cmds)
