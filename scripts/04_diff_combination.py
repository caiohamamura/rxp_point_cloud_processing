#! /usr/bin/env python3

from glob import glob
import argparse
import sys
import itertools
import os
import subprocess
from multiprocessing import Pool

def do_work(cmd):
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    sys.stdout.flush()


def getCmdParser():
    '''
    Get commandline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Makes diff for every combinatorics from a provided glob pattern"))
    p.add_argument(dest="glob_pattern", type=str,
                   help=("Glob pattern to match files to make diff"))
    n_cores = os.cpu_count()
    p.add_argument("-j", "--jobs", dest="threads",
                   type=int, default=(n_cores-1),
                   help=("Glob pattern to match files to make diff"))
    return p


if __name__ == "__main__":
    # read command line
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    previous_path = os.path.abspath(os.path.join(script_path, ".."))

    parser = getCmdParser()
    args = parser.parse_args()

    files = glob(args.glob_pattern)
    if (len(files) == 0):
        print("No files returned from the glob pattern provided!",
              file=sys.stderr)
        sys.exit(1)
    
    combinations = itertools.combinations(files, 2)
    pythonName = "python3"
    if os.name == "nt":
        pythonName = "python"

    cmds = []
    for (file1, file2) in combinations:
        cmd = '"{}" "{}/06_diff_combines.py" "{}" "{}"'.format(
            pythonName, previous_path, file1, file2)
        cmds.append(cmd)
    pool = Pool(args.threads)
    pool.map(do_work, cmds)