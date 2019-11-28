from glob import glob
import os
import subprocess
import sys
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
    p.add_argument("--input", dest="input", default=" ",
                   type=str, help=("Location of the voxelized"))
    cmdargs = p.parse_args()
    return cmdargs


if __name__ == "__main__":
    # read command line
    cmdargs = getCmdArgs()
    inputPath = cmdargs.input
    inputPath = os.path.expanduser(os.path.normpath(inputPath))
    locations = glob(os.path.join(inputPath, "*"))
    cmds = []
    for location in locations:
        basename = os.path.basename(location)
        cmd = "bash 04_combine_list.sh {} {}".format(location, "_" + basename)
        cmds.append(cmd)
    for cmd in cmds:
        try:
            do_work(cmd)
        except:
            pass
