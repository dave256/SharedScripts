#!/usr/bin/env python3

# ----------------------------------------------------------------------
# submissions.py
# Dave Reed
# 12/12/2022
# ----------------------------------------------------------------------

from argparse import ArgumentParser
import glob
import os
import shutil
import zipfile
from RosterInfo import *
from FileUtils import *

def checkZip():
    home = os.getenv("HOME")
    downloads = f"{home}/Downloads"
    zipPath = f"{downloads}/submissions.zip"
    submissionsPath = f"{downloads}/submissions"

    needsUnzipped = False
    if os.path.exists(submissionsPath):
        dirTime = os.path.getmtime(submissionsPath)
        zipTime = os.path.getmtime(zipPath)
        if dirTime < zipTime:
            shutil.rmtree(submissionsPath)
            needsUnzipped = True
    else:
        needsUnzipped = True

    if needsUnzipped:
        with zipfile.ZipFile(zipPath, "r") as infile:
            infile.extractall(downloads)
    else:
        print("does not need unzipped")

def matchFiles(course: Course):
    home = os.getenv("HOME")
    downloads = f"{home}/Downloads"
    submissionsPath = f"{downloads}/submissions"

    os.chdir(submissionsPath)
    files = glob.glob(f"{submissionsPath}/*")
    courseName = course.name().split("-")[0]
    gradePath = FileInfo(home, "Labs", courseName, "Grade")
    shutil.rmtree(gradePath.filePath())
    os.makedirs(gradePath.filePath())

    for f in files:
        filename = FileInfo(f).fileName()
        result = course.findStudentBySubmissionFile(filename)
        if result is not None:
            destDir = FileInfo(gradePath.filePath(), result.email)
            dest = FileInfo(destDir.filePath(), result.filename)
            if not os.path.exists(destDir.filePath()):
                os.makedirs(destDir.filePath())
            # print(f)
            # print(dest.filePath())
            # print()
            shutil.move(f, dest.filePath())
        else:
            print(f"could not process {f}")

    files = glob.glob(f"{submissionsPath}/*")
    if len(files) == 0:
        shutil.rmtree(submissionsPath)
    else:
        print("remaining files")
        for f in files:
            print(f)

def main():
    parser = ArgumentParser(description='extract Canvas submissions')

    # parser.add_argument("-k", "--keep", dest="keepFiles", default=False, action='store_true')
    # parser.add_argument("files", nargs='*', default=None,
    #                     help='''files containing rosters from myCap''')
    parser.add_argument("courseName",
                        help='''name of course from roster''')
    options = parser.parse_args()
    courseName = options.courseName


    # read rosters based on environment variable
    rosterInfo = RosterInfo()
    rosterInfo.readRostersFromEnvironmentVariable("ROSTERS")
    course = rosterInfo.courseWithName(courseName)
    if course is None:
        course = rosterInfo.mergedCourse(courseName)
    if course is None:
        print(f"could not find course {courseName}")
        return

    checkZip()
    matchFiles(course)




# ----------------------------------------------------------------------


if __name__ == '__main__':
    main()
