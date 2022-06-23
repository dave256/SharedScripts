#!/usr/bin/env python3

# ----------------------------------------------------------------------
# myDiff.py
# Dave Reed
# 01/15/2018
# ----------------------------------------------------------------------

import argparse
import os

# ----------------------------------------------------------------------

def stripAndRemoveEmptyLines(lines: list, leadingWhiteSpace: bool = False, blankLinesAtBeginning: bool = False, allBlankLines: bool = False):
    
    for idx, line in enumerate(lines):
        if leadingWhiteSpace:
            line = line.strip()
        else:
            line = line.rstrip()
            
        lines[idx] = line
    
    # remove blank lines at end
    while len(lines) > 0 and lines[-1] == '':
        lines.pop()
    
    # if requested, remove blank lines at beginning
    if blankLinesAtBeginning:
        while len(lines) > 0 and lines[0] == '':
            lines.pop(0)
    
    # if requested, remove all blank lines
    if allBlankLines:
        pos = 0
        while pos < len(lines):
            # if line is blank, remove it and leave pos where it is so check next line which is now at same pos
            if lines[pos] == '':
                lines.pop(pos)
            # otherwise move to next line
            else:
                pos += 1

# ----------------------------------------------------------------------

def diff(f1Lines, f2Lines, args):
    output = False
    f1Length = len(f1Lines)
    f2Length = len(f2Lines)

    for i in range(min(len(f1Lines), len(f2Lines))):
        if f1Lines[i] != f2Lines[i]:
            print(f'line {i+1} differs')
            print(f1Lines[i])
            print(f2Lines[i])
            output = True

    if f1Length > f2Length:
        extra = "\n".join(f1Lines[f2Length:])
        print(f'extra lines in {args.file1}\n{extra}')
        output = True
    elif f2Length > f1Length:
        extra = "\n".join(f2Lines[f1Length:])
        print(f'extra lines in {args.file2}\n{extra}')
        output = True

    # print a blank line at end if we output anything
    if output:
        print()
        

# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='diff ignoring trailing spaces and blank lines at end')
    parser.add_argument('-a', '--all', dest='removeAllBlankLines', action='store_true', help='remove any blank lines')
    parser.add_argument('-b', '--beginning', dest='removeBlankLinesAtBeginning', action='store_true', help='remove blank lines at beginning')
    parser.add_argument('-l', '--leading', dest='leading', action='store_true', help='ignore leading whitespace')
    parser.add_argument('-w', '--write', dest='write', action='store_true', help='write out updated files performing operations specified by flags instead of diffing')
    
    parser.add_argument('file1', type=str)
    parser.add_argument('file2', type=str)
    parser.set_defaults(removeBlankAtBeginning=False, removeAllBlankLines=False, leading=False)
    args = parser.parse_args()
    
    ok = True
    if not os.path.exists(args.file1):
        print(f'{args.file1} does not exist')
        ok = False

    if not os.path.exists(args.file2):
        print(f'{args.file2} does not exist')
        ok = False
    
    if not ok:
        return
    
    # read lines from both files
    with open(args.file1, 'r') as infile:
        f1Lines = infile.readlines()
    with open(args.file2, 'r') as infile:
        f2Lines = infile.readlines()
    
    # remove lines as specified by arguments
    stripAndRemoveEmptyLines(f1Lines, args.leading, args.removeBlankLinesAtBeginning, args.removeAllBlankLines)
    stripAndRemoveEmptyLines(f2Lines, args.leading, args.removeBlankLinesAtBeginning, args.removeAllBlankLines)
    
    # if write argument, write them back out to original files
    if args.write:
        f1String = "\n".join(f1Lines)
        with open(args.file1, 'w') as outfile:
            outfile.writelines(f1String)
        
        f2String = "\n".join(f2Lines)
        with open(args.file2, 'w') as outfile:
            outfile.writelines(f2String)

    else:
        diff(f1Lines, f2Lines, args)
    
# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
