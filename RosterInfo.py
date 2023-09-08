#!/usr/bin/env python3

# ----------------------------------------------------------------------
# RosterInfo.py
# Dave Reed
# 11/25/2019
# ----------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional

import re
import os
import os.path
import csv
import zipfile
import FileUtils


@dataclass
class EmailFile:
    email: str
    filename: str


class Student:

    firstName: str
    lastName: str
    email: str
    courses: List[Course]

    def __init__(self, firstName: str, lastName: str, email: str):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.courses = []

    # ------------------------------------------------------------------

    def addCourse(self, course: Course):
        self.courses.append(course)

    def matchesLastNameFirstName(self, s: str) -> bool:
        """
        :param s: string of the form lastnamefirstname
        :return: True if this student matches that or False otherwise
        """
        s = s.lower()
        last = self.lastName.lower()
        first = self.firstName.lower()
        return s.startswith(last) and s[len(last):].startswith(first)

    # ------------------------------------------------------------------

    def __str__(self):
        return f"{self.firstName} {self.lastName} {self.email} {str(self.courses)}"

# ----------------------------------------------------------------------


class Course:

    _name: str
    _rosterFilename: str
    _students: List[Student]
    # keys are lowercase of last name
    _byLastName: Dict[str, List[Student]]

    def __init__(self, courseWithSection, rosterFileName):
        self._name = courseWithSection
        self._rosterFilename = rosterFileName
        self._students = []
        self._byLastName = {}

    def clone(self) -> Course:
        c = Course(self._name, self._rosterFilename)
        c._students = self._students[:]
        c._byLastName = self._byLastName.copy()
        return c

    def filename(self):
        return self._rosterFilename

    def rosterDirectory(self):
        return os.path.dirname(self._rosterFilename)

    def name(self) -> str:
        return self._name

    def addStudent(self, s: Student):
        self._students.append(s)
        if s.lastName.lower() in self._byLastName:
            self._byLastName[s.lastName.lower()].append(s)
        else:
            self._byLastName[s.lastName.lower()] = [s]

    def students(self) -> List[Student]:
        return self._students

    def studentMatchingLastNameFirstName(self, s: str) -> Optional[Student]:
        for student in self._students:
            if student.matchesLastNameFirstName(s):
                return student
        return None

    def __str__(self) -> str:
        return self._name

    def __lt__(self, other: Course) -> bool:
        return self._name < other._name

    def findStudentBySubmissionFile(self, path: str) -> Optional[EmailFile]:
        firstPos = path.find("_")
        secondPos = path.find("_", firstPos + 1)
        thirdPos = path.find("_", secondPos + 1)

        if firstPos != -1 and secondPos != -1:
            filename = path[thirdPos + 1:]
            # break into name and extension (extension contains the period)
            name, extension = os.path.splitext(filename)
            # check if filename portion ends in "-1", etc. for resubmissions
            dashDigits = re.compile(r"-(\d)+$")
            result = dashDigits.search(name)
            if result is not None:
                # cut off the characters at the end with the dash as they were resubmissions
                name = name[:result.span()[0]]
                filename = name + extension

            user = path[:firstPos].lower()
            for student in self._students:
                if student.matchesLastNameFirstName(user):
                    return EmailFile(student.email, filename)
                # lowerLast = student.lastName.lower()
                # if user.startswith(lowerLast):
                #     # if last name exists
                #     if lowerLast in self._byLastName:
                #         students = self._byLastName[lowerLast]
                #         # if only one student with this last name, found them
                #         if len(students) == 1:
                #             return EmailFile(students[0].email, filename)
                #         else:
                #             # remove lastName from beginning of string
                #             withoutLast = user[len(lowerLast):]
                #             for s in students:
                #                 if withoutLast.startswith(s.firstName.lower()):
                #                     return EmailFile(s.email, filename)
        print(f"couldn't match {path}")
        return None


# ----------------------------------------------------------------------

class RosterInfo:

    lastNameToStudent: Dict[str, Student]
    fullNameToStudent: Dict[str, Student]
    emailToStudent: Dict[str, Student]
    _courses: List[Course]

    def __init__(self):

        self.lastNameToStudent = {}
        self.fullNameToStudent = {}
        self.emailToStudent = {}
        self._courses = []

    # ------------------------------------------------------------------

    def courses(self):
        return self._courses

    # ------------------------------------------------------------------

    def findStudentByName(self, fullName: str):
        # look for paren which may contain what student entered for pronouns
        parenPos = fullName.rfind("(")
        if parenPos != -1:
            # remove the paren and afterwards
            fullName = fullName[:parenPos].strip()

        nameFields = fullName.split()
        if fullName in self.fullNameToStudent:
            return self.fullNameToStudent[fullName]
        # handle pronouns or preferred name that might be there after (
        elif len(nameFields[-1]) > 0 and nameFields[-1][0] == "(":
            del nameFields[-1]
            fullName = " ".join(nameFields)
            if fullName in self.fullNameToStudent:
                return self.fullNameToStudent[fullName]
            
        if self.lastNameToStudent is not None:
            # remove generation value
            if nameFields[-1].upper() in ("II", "III", "IV", "JR", "JR."):
                del nameFields[-1]
            firstName = nameFields[0]
            lastName = nameFields[-1]
            if lastName in self.lastNameToStudent:
                return self.lastNameToStudent[lastName]
            else:
                print(f"{firstName} {lastName} not found")
        print(f"unable to find {fullName}")

    # ------------------------------------------------------------------

    def courseWithName(self, name: str) -> Optional[Course]:
        for c in self._courses:
            if c.name() == name:
                return c
        return None

    # ------------------------------------------------------------------

    def mergedCourse(self, namePrefix: str) -> Optional[Course]:
        result: Optional[Course] = None
        for c in self._courses:
            if c.name().startswith(namePrefix):
                if result is None:
                    result = c.clone()
                else:
                    result._name += f" + {c.name()}"
                    for s in c.students():
                        result.addStudent(s)
        return result

    # ------------------------------------------------------------------

    def findStudentByEmail(self, email):
        return self.emailToStudent[email]

    # ------------------------------------------------------------------

    def courseWithSectionForStudent(self, coursePrefix, student):
        for course in student.courses:
            if course.startswith(coursePrefix):
                return course

    # ------------------------------------------------------------------

    def _addOrUpdateStudent(self, firstName, lastName, email, course):
        fullName = f"{firstName} {lastName}"
        if email in self.emailToStudent:
            s = self.emailToStudent[email]
        elif fullName in self.fullNameToStudent:
            s = self.fullNameToStudent[fullName]
        else:
            s = Student(firstName, lastName, email)
            self.fullNameToStudent[fullName] = s
            self.emailToStudent[email] = s
            # support looking up by last name for last names that do not duplicate
            if lastName not in self.lastNameToStudent:
                self.lastNameToStudent[lastName] = s
            else:
                del self.lastNameToStudent[lastName]

        s.addCourse(course)
        return s

    # ------------------------------------------------------------------
    
    def courseAndFilenames(self):
        return self._courseAndFilenames

    # ------------------------------------------------------------------

    def readRosters(self, courseAndFilenames: tuple):
        self._courseAndFilenames = courseAndFilenames
        for course, filename in courseAndFilenames:
            courseObject = Course(course, filename)
            self._courses.append(courseObject)
            csvReader = csv.reader(filename, delimiter=',')
            lineCount = 0
            headerDict = {}
            with open(filename) as csvFile:
                csvReader = csv.reader(csvFile, delimiter=',')
                for row in csvReader:
                    if lineCount == 0:
                        for index, value in enumerate(row):
                            headerDict[value] = index
                        for field in ("firstName", "first", "First"):
                            try:
                                firstNameIndex = headerDict[field]
                            except:
                                pass
                        for field in ("lastName", "last", "Last"):
                            try:
                                lastNameIndex = headerDict[field]
                            except:
                                pass
                        for field in ("primaryEmail", "Email", "email1"):
                            try:
                                emailIndex = headerDict[field]
                            except:
                                pass
                    else:
                        if len(row) > 0:
                            firstName = row[firstNameIndex]
                            lastName = row[lastNameIndex]
                            email = row[emailIndex]
                            s = self._addOrUpdateStudent(firstName, lastName, email, course)
                            courseObject.addStudent(s)

                    lineCount += 1

    # ------------------------------------------------------------------

    def determineCourse(self, zipPath: str) -> Optional[str]:
        """
        tries to determine course based on student filenames in zip file
        if finds, returns something such as CS261-9 (or CS261 if students from multiple sections of CS261)
        :param zipPath: path to the zip file
        :return: courseName if found or None if couldn't determine
        """
        with zipfile.ZipFile(zipPath, "r") as infile:
            infoList: List[zipfile.ZipInfo] = infile.infolist()
            filenames = [FileUtils.FileInfo(info.filename).fileName() for info in infoList]
            # get filenames that are not empty and don't start with a period
            filenames = [s for s in filenames if s != "" and s[0] != "."]
            # get everything up to first underscore which should be lastfirst for the person
            users = set([s.split("_")[0] for s in filenames])
            courseDict = {}
            for c in self._courses:
                courseDict[c.name()] = set()
                for user in users:
                    student: Optional[Student] = c.studentMatchingLastNameFirstName(user)
                    if student is not None:
                        courseDict[c.name()].add(student)

            nonZero = []
            for courseName in courseDict:
                if len(courseDict[courseName]) > 0:
                    nonZero.append(courseName)

            mergedCourses = dict()
            if len(nonZero) == 1:
                return nonZero[0]
            else:
                result = set()
                for name in nonZero:
                    # remove section and add to set
                    prefix = name.split("-")[0]
                    if prefix in result:
                        mergedCourses[prefix].update(courseDict[name])
                    else:
                        mergedCourses[prefix] = courseDict[name].copy()
                    result.add(prefix)

                if len(result) == 1:
                    return result.pop()

            # try to match the course with the higher count
            # a better approach would be to match the course with a higher percentage
            # of submissions
            maxCount = 0
            maxCourse = None
            for course in mergedCourses:
                if len(mergedCourses[course]) > maxCount:
                    maxCourse = course
                    maxCount = len(mergedCourses[course])
            if maxCount > 0:
                return maxCourse
            return None

    # ------------------------------------------------------------------

    def readRostersFromEnvironmentVariable(self, envVar):
        try:
            info = os.getenv(envVar)
        except:
            print(f"{envVar} environment variable not set")
            return

        info = info.split(":")

        # turn environment variable that has courseName:pathToRosterFile:courseName:pathToRosterFile
        # into ((courseName, pathToRosterFile), (courseName, pathToRosterFile))
        courseAndFilenames = tuple(zip(*(iter(info),) * 2))
        self.readRosters(courseAndFilenames)

# ----------------------------------------------------------------------

        