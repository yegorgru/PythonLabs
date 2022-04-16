from helper import Helper
from logger import Logger
from utils import parseOptions
from utils import yesNoDialog
from unit import Unit
from employee import Employee

import sqlite3

from enum import Enum
import os.path
import sys

helpDict = {
    "help": "print help logger.info",
    "create [FILE]": "create new database",
    "connect [FILE]": "connect to database",
    "save": "save file",
    "undo changes": "undo changes",
    "add unit": ("add new unit", {"-n[NAME]": "unit name"}),
    "add employee": ("add new employee", {"-n[NAME]": "employee name", "-u[ID]": "unit id", "-r[RANK]": "employee's rank", "-e[EXPERIENCE]": "employee's experience"}),
    "update unit [UNIT ID]": ("update unit logger.info", {"-n[NAME]": "update name"}),
    "update employee [EMPLOYEE ID]": ("update employee's logger.info", {"-n[NAME]": "update name", "-u[ID]": "update unit id", "-r[RANK]": "update rank", "-e[EXPERIENCE]": "update experience"}),
    "delete unit [UNIT_ID]": "delete unit",
    "delete employee [EMPLOYEE_ID]": "delete employee",
    "select units": ("print units logger.info", {"-i[UNIT_ID]": "find by id", "n[NAME]": "find by name"}),
    "select employees": ("print employees logger.info", {"-i[EMPLOYEE_ID]": "find by id", "-n[NAME]": "find by name", "-r[RANK]": "find by rank", "-e[EXPERIENCE]": "find by experience", "-u[UNIT_ID]": "find by unit id"}),
    "stat": ("print statistics", {"-u": "print units order by number of employees", "-r": "print employees order by rank", "-e": "print employees order by experience"}),
    "q": "exit"
}

helper = Helper(helpDict)

class State(Enum):
	EMPTY = 0,
	UNSAVED_CHANGES = 1,
	SAVED_CHANGES = 2

class HumanResourcesManager:
	__conn = None
	__cur = None

	def __init__(self):
		self.__setState(State.EMPTY)
		self.__currentFile = ""

	def __setState(self, state):
		if type(state) != State:
			logger.ERROR("state must be State")
			exit()
		self.__state = state

	def getState(self):
		return self.__state

	def __setCurrentFile(self, file):
		if type(file) != str:
			logger.ERROR("file must be str")
			exit()
		self.__currentFile = file

	def getCurrentFile(self):
		return self.__currentFile

	def insertEmployee(self, employee):
		if not self.checkEmpty(): return
		self.__cur.execute("SELECT COUNT() FROM Employee")
		numberOfRows = self.__cur.fetchone()[0]
		if numberOfRows == 0:
			id = 0;
		else:
			self.__cur.execute("SELECT MAX(ID) FROM Employee")
			id = self.__cur.fetchone()[0] + 1
		self.__cur.execute('''INSERT INTO Employee (ID, NAME, RANK, EXPERIENCE, UNIT_ID) 
			VALUES ( ?, ?, ?, ?, ? )''', ( id, employee.getName(), employee.getRank(), employee.getExperience(), employee.getUnitId()) )
		self.__setState(State.UNSAVED_CHANGES)
		return id

	def insertUnit(self, unit):
		if not self.checkEmpty(): return
		self.__cur.execute("SELECT COUNT() FROM Unit")
		numberOfRows = self.__cur.fetchone()[0]
		if numberOfRows == 0:
			id = 0;
		else:
			self.__cur.execute("SELECT MAX(ID) FROM Unit")
			id = self.__cur.fetchone()[0] + 1
		self.__cur.execute('''INSERT INTO Unit (ID, NAME) 
			VALUES ( ?, ? )''', ( id, unit.getName()) )
		self.__setState(State.UNSAVED_CHANGES)
		return id

	def statU(self):
		self.__cur.execute('''SELECT e.UNIT_ID, u.NAME, COUNT()
			FROM Employee e
			INNER JOIN Unit u
			ON u.ID = e.UNIT_ID
			GROUP BY u.ID
			ORDER BY COUNT() DESC
			''')
		for value in self.__cur.fetchall():
			print("Unit id:", value[0], "name:", value[1], "number of employees:", value[2])

	def statR(self):
		self.__cur.execute('''SELECT ID, NAME, RANK
			FROM Employee
			ORDER BY RANK DESC
			''')
		for value in self.__cur.fetchall():
			print("Employee id:", value[0], "name:", value[1], "rank:", value[2])

	def statE(self):
		self.__cur.execute('''SELECT ID, NAME, EXPERIENCE
			FROM Employee
			ORDER BY EXPERIENCE DESC
			''')
		for value in self.__cur.fetchall():
			print("Employee id:", value[0], "name:", value[1], "experience:", value[2])

	def checkEmpty(self):
		if self.__state == State.EMPTY:
			logger.ERROR("not connected to database")
			return False;
		return True

	def suggestSave(self):
		if self.__state == State.UNSAVED_CHANGES:
			logger.WARNING("You have unsaved changes, save it? [y/n]")
			answer = yesNoDialog()
			if answer:
				self.save()

	def __clean(self):
		self.__setState(State.EMPTY)
		if self.__currentFile != "":
			self.__conn.close()
		self.__setCurrentFile("")

	def save(self):
		if not self.checkEmpty(): return
		self.__conn.commit()
		self.__setState(State.SAVED_CHANGES)
		logger.INFO("data saved")

	def undoChanges(self):
		if not self.checkEmpty(): return
		self.__conn.rollback()
		self.__setState(State.SAVED_CHANGES)
		logger.INFO("data rolled back")

	def connect(self, file):
		self.suggestSave()
		self.__clean()
		if not os.path.isfile(file):
			logger.ERROR("incorrect path")
			return;
		self.__setCurrentFile(file)
		self.__conn = sqlite3.connect(file)
		self.__cur = self.__conn.cursor()
		self.__setState(State.SAVED_CHANGES)

	def create(self, file):
		if file == "":
			logger.ERROR("empty file name")
			return;
		elif os.path.isfile(file):
			logger.ERROR("file already exists")
			return;
		newConn = sqlite3.connect(file)
		newCur = newConn.cursor()
		newCur.execute('''CREATE TABLE \"Unit\" (
			\"ID\"	INTEGER NOT NULL UNIQUE,
			\"NAME\"	TEXT,
			PRIMARY KEY(\"ID\")
		)''')
		newCur.execute('''CREATE TABLE \"Employee\" (
			\"ID\"	INTEGER NOT NULL UNIQUE,
			\"NAME\"	INTEGER,
			\"EXPERIENCE\"	INTEGER,
			\"RANK\"	INTEGER,
			\"UNIT_ID\"	INTEGER,
			PRIMARY KEY(\"ID\")
		)''')
		newConn.commit()
		newConn.close()
		self.connect(file)

	def selectEmployees(self, options):
		self.checkEmpty()
		statement = '''SELECT ID, NAME, RANK, EXPERIENCE, UNIT_ID FROM Employee '''
		if len(options) != 0:
			statement = statement + "WHERE "
			needAnd = False
			if "i" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "ID = " + options["i"] + " "
				needAnd = True
			if "u" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "UNIT_ID = " + options["u"] + " "
				needAnd = True
			if "r" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "RANK = " + options["r"] + " "
				needAnd = True
			if "e" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "EXPERIENCE = " + options["e"] + " "
				needAnd = True
			if "n" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "NAME = " + "\'" + options["n"] + "\' "
				needAnd = True
		self.__cur.execute(statement)
		for value in self.__cur.fetchall():
			print("ID:", value[0], "name:", value[1], "rank:", value[2], "experience:", value[3], "unit id:", value[4])

	def selectUnits(self, options):
		self.checkEmpty()
		statement = '''SELECT ID, NAME FROM Unit '''
		if len(options) != 0:
			statement = statement + "WHERE "
			needAnd = False
			if "i" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "ID = " + options["i"] + " "
				needAnd = True
			if "n" in options:
				if needAnd:
					statement = statement + "AND "
				statement = statement + "NAME = " + "\'" + options["n"] + "\' "
				needAnd = True
		self.__cur.execute(statement)
		for value in self.__cur.fetchall():
			print("ID:", value[0], "name:", value[1])

	def updateEmployee(self, id, options):
		self.checkEmpty()
		statement = '''UPDATE Employee SET '''
		if not "u" in options and not "r" in options and not "e" in options and not "n" in options:
			logger.WARNING("Nothing to update")
			return
		needComma = False
		if "u" in options:
			if needComma:
				statement = statement + ", "
			statement = statement + "UNIT_ID = " + options["u"] + " "
			needComma = True
		if "r" in options:
			if needComma:
				statement = statement + ", "
			statement = statement + "RANK = " + options["r"] + " "
			needComma = True
		if "e" in options:
			if needComma:
				statement = statement + ", "
			statement = statement + "EXPERIENCE = " + options["e"] + " "
			needComma = True
		if "n" in options:
			if needComma:
				statement = statement + ", "
			statement = statement + "NAME = " + "\'" + options["n"] + "\' "
			needComma = True
		statement = statement + "WHERE ID = " + id
		try:
			self.__cur.execute(statement)
			self.__setState(State.UNSAVED_CHANGES)
		except:
			logger.ERROR("Failed to update value. Possible reason: incorrect ID")

	def updateUnit(self, id, options):
		self.checkEmpty()
		statement = '''UPDATE Unit SET '''
		if not "n" in options:
			logger.WARNING("Nothing to update")
			return
		statement = statement + "NAME = " + "\'" + options["n"] + "\' "
		statement = statement + "WHERE ID = " + id
		try:
			self.__cur.execute(statement)
			self.__setState(State.UNSAVED_CHANGES)
		except:
			logger.ERROR("Failed to update value. Possible reason: incorrect ID")

	def deleteEmployee(self, id):
		self.checkEmpty()
		statement = "DELETE FROM Employee WHERE ID = " + id
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def deleteUnit(self, id):
		self.checkEmpty()
		statement = "DELETE FROM Unit WHERE ID = " + id
		self.__cur.execute(statement)
		statement = "DELETE FROM Employee WHERE UNIT_ID = " + id
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def checkUnit(self, id):
		self.checkEmpty()
		self.__cur.execute("SELECT COUNT() FROM Unit WHERE ID=" + str(id))
		if self.__cur.fetchone()[0] == 0:
			return False
		else:
			return True

if "-d" in sys.argv:
	logger = Logger(True);
else:
	logger = Logger(False);
manager = HumanResourcesManager()
while True:
	if manager.getCurrentFile() != "":
		hint = "[" + manager.getCurrentFile() + "]: "
	else:
		hint = ""
	command = input(hint)
	words = command.split()
	options = parseOptions(words)
	if command == "":
		continue
	elif command == "q":
		manager.suggestSave()
		exit()
	elif command == "help":
		helper.printHelpInfo()
	elif words[0] == "connect":
		if len(words) != 2:
			logger.ERROR("Incorrect use of connect. Help:")
			helper.printHelpCommand("connect [FILE]")
		else:
			manager.connect(words[1])
	elif words[0] == "create":
		if len(words) != 2:
			logger.ERROR("Incorrect use of create. Help:")
			helper.printHelpCommand("create [FILE]")
		else:
			manager.create(words[1])
	elif command == "save":
		manager.save()
	elif command == "undo changes":
		manager.undoChanges()
	elif len(words) >= 2 and words[0] == "add" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		try:
			logger.DEBUG("create unit " + options["n"])
			id = manager.insertUnit(Unit(options["n"]))
			logger.INFO("Create unit. Id: " + str(id))
		except:
			logger.ERROR("Failed to add unit. Help:")
			helper.printHelpCommand("add unit")
	elif len(words) >= 2 and words[0] == "add" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		try:
			unitId = int(options["u"])
			if not manager.checkUnit(unitId):
				logger.ERROR("Incorrect unit id")
				continue
			id = manager.insertEmployee(Employee(unitId, options["n"], int(options["r"]), int(options["e"])))
			logger.INFO("Create employee. Id: " + str(id))
		except:
			logger.ERROR("Failed to add employee. Help:")
			helper.printHelpCommand("add employee")
	elif len(words) >= 2 and words[0] == "update" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		if len(words) < 3:
			logger.ERROR("Incorrect use of update unit. Help:")
			helper.printHelpCommand("update unit [UNIT ID]")
			continue;
		try:
			id = words[2]
			manager.updateUnit(id, options)
			logger.INFO("Update unit " + str(id))
		except:
			logger.ERROR("Failed to update unit. Help:")
			helper.printHelpCommand("update unit [UNIT ID]")
	elif len(words) >= 2 and words[0] == "update" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		if len(words) < 3:
			logger.ERROR("Incorrect use of update employee. Help:")
			helper.printHelpCommand("update employee [EMPLOYEE ID]")
			continue;
		try:
			if "u" in options:
				unitId = int(options["u"])
				if not manager.checkUnit(unitId):
					logger.ERROR("Incorrect unit id")
					continue
			id = words[2]
			manager.updateEmployee(id, options)
			logger.INFO("Update employee " + str(id))
		except:
			logger.ERROR("Failed to update employee. Help:")
			helper.printHelpCommand("update employee [EMPLOYEE ID]")
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			logger.ERROR("Incorrect use of delete unit. Help:")
			helper.printHelpCommand("delete unit [UNIT_ID]")
		try:
			id = words[2]
			manager.deleteUnit(id)
			logger.INFO("Delete unit " + id)
		except:
			logger.ERROR("Failed to delete unit. Help:")
			helper.printHelpCommand("delete unit [UNIT_ID]")
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			logger.ERROR("Incorrect use of delete employee. Help:")
			helper.printHelpCommand("delete employee [EMPLOYEE_ID]")
		try:
			id = words[2]
			manager.deleteEmployee(id)
			logger.INFO("Delete employee " + id)
		except:
			logger.ERROR("Failed to delete employee. Help:")
			helper.printHelpCommand("delete employee [EMPLOYEE_ID]")
	elif len(words) >= 2 and words[0] == "select" and words[1] == "units":
		if not manager.checkEmpty(): continue
		manager.selectUnits(options)
	elif len(words) >= 2 and words[0] == "select" and words[1] == "employees":
		if not manager.checkEmpty(): continue
		manager.selectEmployees(options)
	elif words[0] == "stat":
		try:
			if not manager.checkEmpty(): continue
			if "-u" in words:
				manager.statU()
			if "-r" in words:
				manager.statR()
			if "-e" in words:
				manager.statE()
		except:
			logger.ERROR("Failed to print statistics. Help:")
			helper.printHelpCommand("stat")
	else:
		logger.ERROR("Unknown command")
