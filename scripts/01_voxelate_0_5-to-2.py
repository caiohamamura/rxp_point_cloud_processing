#!/usr/bin/env python3

from multiprocessing import Pool
from glob import glob
import pandas as pd
import os
import sys
import numpy as np
import subprocess
import argparse

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


def execute(command):
    subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)



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

    # Main loop
    columns = ['input', 'output', 'transform_matrix']
    cmds = []
    steps = np.arange(0.5, 2.1, 0.25)
    #steps = np.hstack([[0.3], steps])
    for i in steps:
        out_path_res = os.path.join(out_path, str(i))
        try:
            os.mkdir(out_path_res)
        except FileExistsError:
            pass

        # Build the command
        cmd = 'python3 03_voxelize.py "{}" "{}" "{}" {} -j{}'.format(
            in_path, out_path_res, os.path.basename(csv_file), i, n_cores)
        if (args.z_min != -9999 or args.z_max != -9999):
            cmd = '{} --z_min {} --z_max {}'.format(
                cmd, args.z_min, args.z_max)
        cmds.append(cmd)
    # Run the commands in parallel
    os.chdir(os.path.dirname(os.path.abspath(csv_file)))
    for cmd in cmds:
        execute(cmd)
        sys.stdout.flush()
