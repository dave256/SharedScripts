#!/usr/bin/env python3

# ----------------------------------------------------------------------
# rosters.py
# Dave Reed
# 05/29/2020
# ----------------------------------------------------------------------


from argparse import ArgumentParser
import glob
import os

def readEnvVar(envVar="ROSTERS"):
    try:
        info = os.getenv(envVar)
    except:
        print(f"{envVar} environment variable not set")
        return

    info = info.split(":")

    # turn environment variable that has courseName:pathToRosterFile:courseName:pathToRosterFile
    # into ((courseName, pathToRosterFile), (courseName, pathToRosterFile))
    courseAndFilenames = tuple(zip(*(iter(info),) * 2))
    courseDict = {}
    for course, filename in courseAndFilenames:
        courseDict[course] = filename
    return courseDict

# ----------------------------------------------------------------------

def readCourseSections(envVar="COURSESECTIONS"):
    try:
        info = os.getenv(envVar)
    except:
        print(f"{envVar} environment variable not set")
        return
    
    info = info.split(":")

    sections = tuple(zip(*(iter(info),) * 2))
    sectionDict = {}
    for section, courseTime in sections:
        sectionDict[section] = courseTime
    return sectionDict
    
# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='look for myCap roster files named section-rosters and create roster.csv and ga.csv files; mv them to appropriate directory based on ROSTERS environment variable')

    parser.add_argument("-k", "--keep", dest="keepFiles", default=False, action='store_true')
    parser.add_argument("files", nargs='*', default=None,
                        help='''files containing rosters from myCap''')
    options = parser.parse_args()

    files = options.files
    keepFiles = options.keepFiles
    
    homeDir = os.getenv("HOME")
    # look for files in downloads directory if not provided on command line
    if files is None or len(files) == 0:
        files = glob.glob(f"{homeDir}/Downloads/section-rosters*.csv")

    files.sort()
    outputLines = []
    
    courseDict = readEnvVar()
    # save since we remove them from courseDict as we match them up
    envDict = courseDict.copy()
    
    sectionDict = readCourseSections()
    
    for f in files:
        courseSection = None
        courseNumber = None
        pos = f.find("CS-")
        if pos != -1:
            courseSection = f[pos:pos+9]
            courseNumber = courseSection[:6].replace("-", "")
            courseSection = courseSection.replace("CS-", "CS")
        else:
            pos = f.find("MATH-")
            if pos != -1:
                courseSection = f[pos:pos+11]
                courseNumber = courseSection[:8].replace("-", "")
                courseSection = courseSection.replace("MATH-", "MATH")
            else:
                pos = f.find("UC-")
        isMath = courseNumber.find("MATH") != -1

        possibleCourses = []
        for course in courseDict:
            if isMath:
                if courseNumber == course[:7]:
                    possibleCourses.append(course)
                elif courseNumber.replace("MATH", "MA") == course[:5]:
                    possibleCourses.append(course)
                elif courseNumber.replace("MATH", "CS") == course[:5]:
                    possibleCourses.append(course)
            else:
                if courseNumber == course[:5]:
                    possibleCourses.append(course)
        
        
        if len(possibleCourses) > 1:
            if courseSection in sectionDict:
                # use COURSESECTIONS env var to pick time
                selectedCourse = sectionDict[courseSection]
            else:
                # have user enter matching time
                print()
                print(f.split(os.sep)[-1])
                for i, p in enumerate(possibleCourses):
                    print(f"{i+1} : {p}")
                n = int(input("enter choice: "))
                selectedCourse = possibleCourses[n - 1]
        else:
            selectedCourse = possibleCourses[0]
        
        lastPath = f[f.rfind(os.sep)+1:]
        outputLines.append(f"{lastPath} -> {selectedCourse}")
        
        # remove sections we've already matched except for seminar
        if not isMath and selectedCourse[:5] != "CS481":
            del courseDict[selectedCourse]
        
        destDir = envDict[selectedCourse]
        destDir = destDir[:destDir.rfind(os.sep)]

        #cmd = f"$HOME/Scripts/myCap.py '{f}'"
        # so can work if mycap.py is in PATH with my SharedScripts repo
        cmd = f"myCap.py '{f}'"
        os.system(cmd)
        if not isMath:
            cmd = f"mv roster.csv {envDict[selectedCourse]}"
        else:
            cmd = f"mv roster.csv {destDir}/math-roster.csv"
        os.system(cmd)
        
        #cmd = f"$HOME/Scripts/myCap2ga.py '{f}'"
        # so can work if mycap.py is in PATH with my SharedScripts repo
        cmd = f"myCap2ga.py '{f}'"
        os.system(cmd)
        if not isMath:
            cmd = f"mv ga.csv {destDir}/ga.csv"
        else:
            cmd = f"mv ga.csv {destDir}/math-ga.csv"
        os.system(cmd)

    print()
    print("\n".join(outputLines))

    if not keepFiles:
        for f in files:
            os.remove(f)
    
# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
