#!/usr/bin/env python3

from multiprocessing import Pool
from glob import glob
import pandas as pd
import os
import sys
import numpy as np
import subprocess

def execute(command):
    subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)




def parse_error(error):
    sys.stderr.write("{}!\nUsage: 'python3 {} <input_path> <output_path> \
<csv_file>  <n_cores>'\n".format(
        error, sys.argv[0]))
    sys.exit(-1)


def input_args_checking_return_cores(n_args):
    n = 1

    if (len(sys.argv) != n_args+1):
        parse_error("Wrong number of inputs")

    try:
        n = int(sys.argv[n_args])
    except:
        parse_error("Number of cores is not a number")

    if (not os.path.isdir(os.path.expanduser(sys.argv[1]))):
        parse_error("Input path is not a valid path")
    if (not os.path.isdir(os.path.expanduser(sys.argv[2]))):
        parse_error("Output path is not a valid path")
    if (not os.path.isfile(os.path.expanduser(sys.argv[3]))):
        parse_error("CSV path is not a valid")

    return n


if __name__ == '__main__':
    n_args = 4

    n_cores = input_args_checking_return_cores(n_args)

    in_path = os.path.expanduser(sys.argv[1])
    out_path = os.path.expanduser(sys.argv[2])
    csv_file = os.path.expanduser(sys.argv[3])

    # Main loop
    columns = ['input', 'output', 'transform_matrix']
    cmds = []
    for i in np.arange(0.5, 2.1, 0.25):
        out_path_res = os.path.join(out_path, str(i))
        try:
            os.mkdir(out_path_res)
        except FileExistsError:
            pass

        # Build the command
        cmd = 'python3 03_voxelize.py "{}" "{}" "{}" "{}" {}'.format(
            in_path, out_path_res, os.path.basename(csv_file), i, n_cores)
        cmds.append(cmd)
    # Run the commands in parallel
    os.chdir(os.path.dirname(csv_file))
    for cmd in cmds:
        execute(cmd)
        sys.stdout.flush()
