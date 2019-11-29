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


if __name__ == "__main__":
    files = glob("results/d?l*.txt")
    cmds = []
    for file in files:
        basename, ext = os.path.splitext(file)
        cmd = "python3 05_combine.py --inList {} --output {}.csv.gz --minGap 0.001".format(file, basename)
        cmds.append(cmd)
    print(cmds)
    pool = Pool(10)
    pool.map(do_work, cmds)
