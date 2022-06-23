#!/usr/bin/env python3

# ----------------------------------------------------------------------
# mycap2ga.py
# Dave Reed
# 01/02/2020
# ----------------------------------------------------------------------

import sys
import csv
from myDiff import stripAndRemoveEmptyLines

# ----------------------------------------------------------------------

def main(argv):

    if len(argv) == 1:
        ifname = input('enter filename: ')
    else:
        ifname = argv[1]
        
    nameKey = 'Student Name'
    emailKey = 'Preferred Email'
    identifierKey = 'Student ID'
    noteKey = 'Class Level'
    
    if 'ga' in argv[0]:
        headerLine = 'Last,First,Middle,Email,ID,Note'
        ofname = 'ga.csv'
    else:
        headerLine = 'lastName,firstName,middleName,primaryEmail,identifier,note'
        ofname = 'roster.csv'
        
    with open(ofname, 'w') as outfile:
        print(headerLine, file=outfile)
        
        with open(ifname) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row[nameKey].replace(",", " ")
                email = row[emailKey]
                identifier = row[identifierKey]
                note = row[noteKey].replace(",", " ")
                nameFields = name.split()
                if nameFields[-1].upper() in ("II", "III", "IV", "JR", "JR."):
                    del nameFields[-1]
                if len(nameFields) == 2:
                    firstName = nameFields[0]
                    middleName = ""
                    lastName = nameFields[1]
                elif len(nameFields) == 3:
                    firstName = nameFields[0]
                    middleName = nameFields[1]
                    lastName = nameFields[2]
                else:
                    firstName = nameFields[0]
                    lastName = nameFields[-1]
                    middleName = " ".join(nameFields[1:-1])
                    
                print(f"{lastName},{firstName},{middleName},{email},{identifier},{note}", file=outfile)

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
