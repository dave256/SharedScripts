#!/usr/bin/env python3

#----------------------------------------------------------------------
# run_dir.py
# Dave Reed
# 04/09/2005
#----------------------------------------------------------------------

import os, sys, os.path

#----------------------------------------------------------------------

def main(argv):

    run_com = argv[1]
    dirs = argv[2:]
    for d in dirs:
        if os.path.isdir(d):
            print('d: ', d)
            com = f"cd {d}; {run_com}"
            print(com)
            os.system(com)

#----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
