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


def checkZip() ->str:
    """
    :return: full path of submissions.zip
    """
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
            infile.extractall(submissionsPath)
    else:
        print("does not need unzipped")
    return zipPath


def matchFiles(course: Course):
    home = os.getenv("HOME")
    downloads = f"{home}/Downloads"
    submissionsPath = f"{downloads}/submissions"

    os.chdir(submissionsPath)
    files = glob.glob(f"{submissionsPath}/*")
    courseName = course.name().split("-")[0]
    gradePath = FileInfo(home, "Labs", courseName, "Grade")
    shutil.rmtree(gradePath.filePath(), True)
    os.makedirs(gradePath.filePath())

    for f in files:
        # Canvas adds _LATE_ as part of filename so remove it if it's there
        if "_LATE_" in f:
            newName = f.replace("_LATE_", "_")
            os.rename(f, newName)
            f = newName
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

    parser.add_argument("-k", "--keep", dest="keepFiles", default=False, action='store_true')
    parser.add_argument("courseNames", nargs='*', default=None,
                        help='''course names matching environment variables for courses
examples: 
submissions.py CS410 or
submissions.py CS160-12 CS160-1
                ''')
    options = parser.parse_args()

    # read rosters based on environment variable
    rosterInfo = RosterInfo()
    rosterInfo.readRostersFromEnvironmentVariable("ROSTERS")

    courseName = None
    if options.courseNames is not None and len(options.courseNames) == 1:
        courseName = options.courseNames[0]
    else:
        home = os.getenv("HOME")
        downloads = f"{home}/Downloads"
        zipPath = f"{downloads}/submissions.zip"
        courseName = rosterInfo.determineCourse(zipPath)

    if courseName is None:
        print(f"could not find course {courseName}")
        return

    course = rosterInfo.courseWithName(courseName)
    if course is None:
        course = rosterInfo.mergedCourse(courseName)

    # indicate which course
    if course is None:
        print("stopping as could not find course")
        return
    else:
        print(f"unzipping for {course}")

    zipPath = checkZip()
    matchFiles(course)

    # remove submissions.zip unless keep flag specified
    if not options.keepFiles:
        os.remove(zipPath)

# ----------------------------------------------------------------------


if __name__ == '__main__':
    main()
