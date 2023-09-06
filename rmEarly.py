#!/usr/bin/env python3

# ----------------------------------------------------------------------
# rmEarly.py
# Dave Reed
# 09/06/2023
# ----------------------------------------------------------------------

from argparse import ArgumentParser
import glob
import os
import shutil

from FileUtils import *


def main():
    parser = ArgumentParser(description='''
    delete early submissions
    use from ~/Labs/<courseDir>; 
    by default it removes any directories in Grade directory that are also in Early directory;
    can specify the directories with -e and -d''')

    parser.add_argument("-e", "--earlyDirectory", dest="earlyDirectory", default='Early')
    parser.add_argument("-d", "--directory", dest="directory", default='Grade')

    options = parser.parse_args()

    earlyDir = options.earlyDirectory
    directory = options.directory

    earlyDirectories = [FileInfo(d).fileName() for d in DirectoryInfo(earlyDir).directories()]

    directoryPaths = DirectoryInfo(directory).directories()
    for path in directoryPaths:
        d = FileInfo(path).fileName()
        if d in earlyDirectories:
            print(f"/bin/rm -rf {path}")
            shutil.rmtree(path)

# ----------------------------------------------------------------------


main()
