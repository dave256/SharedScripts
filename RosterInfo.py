#!/usr/bin/env python3

# ----------------------------------------------------------------------
# RosterInfo.py
# Dave Reed
# 11/25/2019
# ----------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional

import os
import os.path
import csv

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
            user = path[:firstPos].lower()
            for student in self._students:
                lowerLast = student.lastName.lower()
                if user.startswith(lowerLast):
                    # if last name exists
                    if lowerLast in self._byLastName:
                        students = self._byLastName[lowerLast]
                        # if only one student with this last name, found them
                        if len(students) == 1:
                            return EmailFile(students[0].email, filename)
                        else:
                            # remove lastName from beginning of string
                            withoutLast = user[len(lowerLast):]
                            for s in students:
                                if withoutLast.startswith(s.firstName.lower()):
                                    return EmailFile(s.email, filename)
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

        