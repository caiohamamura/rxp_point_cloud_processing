from glob import glob
import os
import subprocess
import sys
from multiprocessing import Pool   
import argparse

def do_work(cmd):
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    sys.stdout.flush()

def getCmdArgs():
    '''
    Get commdnaline arguments
    '''
    p = argparse.ArgumentParser(description=(
        "Combines voxel PAI estimates from multiple scans"))
    p.add_argument("glob_pattern",
                   type=str,
                   help="Glob pattern to search for files")

    p.add_argument("-j", "--jobs", dest="threads", type=int,
                   default=os.cpu_count()-1,
                   help="Number of jobs to run in parallel")

    p.add_argument("-g", "--min_gap", dest="min_gap",
                   type=int, default=0.001,
                   help="Minimum gap fraction")
    args = p.parse_args()
    return args


if __name__ == "__main__":
    args = getCmdArgs()
    files = glob(args.glob_pattern)
    if len(files) == 0:
        print("Glob pattern won't match any file", file=sys.stderr)
        sys.exit(1)

    cmds = []
    for file in files:
        basename, ext = os.path.splitext(file)
        cmd = "python3 05_combine.py --inList {} --output {}.csv.gz \
--minGap {}".format(file, basename, args.min_gap)
        cmds.append(cmd)
    print(cmds)
    pool = Pool(args.threads)
    pool.map(do_work, cmds)
