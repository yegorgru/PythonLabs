from unit import Unit
from employee import Employee
from utils import parseOptions

import sqlite3
from enum import Enum
import os.path

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
		self.__state = state

	def getState(self):
		return self.__state

	def __setCurrentFile(self, file):
		self.__currentFile = file

	def getCurrentFile(self):
		return self.__currentFile

	def insertEmployee(self, employee):
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
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "Unit id: " + str(value[0]) + " name: " + value[1] + " number of employees: " + str(value[2])
		message = "TEXT" + '#' + output
		return message

	def statR(self):
		self.__cur.execute('''SELECT ID, NAME, RANK
			FROM Employee
			ORDER BY RANK DESC
			''')
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "Employee id: " + str(value[0]) + " name: " + value[1] + " rank: " + str(value[2])
		message = "TEXT" + '#' + output
		return message

	def statE(self):
		self.__cur.execute('''SELECT ID, NAME, EXPERIENCE
			FROM Employee
			ORDER BY EXPERIENCE DESC
			''')
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "Employee id: " + str(value[0]) + " name: " + value[1] + " experience: " + str(value[2])
		message = "TEXT" + '#' + output
		return message

	def __clean(self):
		self.__setState(State.EMPTY)
		if self.__currentFile != "":
			self.__conn.close()
		self.__setCurrentFile("")

	def save(self):
		if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
		self.__conn.commit()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "data saved"
		return message

	def undoChanges(self):
		if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
		self.__conn.rollback()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "data rolled back"
		return message

	def connect(self, file):
		self.__clean()
		if not os.path.isfile(file):
			message = "ERROR" + '#' + "incorrect path"
			return message
			return;
		self.__setCurrentFile(file)
		self.__conn = sqlite3.connect(file)
		self.__cur = self.__conn.cursor()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "connected to " + file
		return message

	def create(self, file):
		if file == "":
			message = "ERROR" + '#' + "empty file name"
			return message
			return;
		elif os.path.isfile(file):
			message = "ERROR" + '#' + "file already exists"
			return message
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
		return self.connect(file)

	def selectEmployees(self, options):
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
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "ID: " + str(value[0]) + " name: " + value[1] + " rank: " + str(value[2]) +  " experience: " + str(value[3]) + " unit id: " + str(value[4])
		message = "TEXT" + '#' + output
		return message

	def selectUnits(self, options):
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
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "ID: " + str(value[0]) + " name: " + value[1]
		message = "TEXT" + '#' + output
		return message

	def updateEmployee(self, id, options):
		statement = '''UPDATE Employee SET '''
		if not "u" in options and not "r" in options and not "e" in options and not "n" in options:
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
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def updateUnit(self, id, options):
		statement = '''UPDATE Unit SET '''
		if not "n" in options:
			return
		statement = statement + "NAME = " + "\'" + options["n"] + "\' "
		statement = statement + "WHERE ID = " + id
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def deleteEmployee(self, id):
		statement = "DELETE FROM Employee WHERE ID = " + id
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def deleteUnit(self, id):
		statement = "DELETE FROM Unit WHERE ID = " + id
		self.__cur.execute(statement)
		statement = "DELETE FROM Employee WHERE UNIT_ID = " + id
		self.__cur.execute(statement)
		self.__setState(State.UNSAVED_CHANGES)

	def checkUnit(self, id):
		self.__cur.execute("SELECT COUNT() FROM Unit WHERE ID=" + str(id))
		if self.__cur.fetchone()[0] == 0:
			return False
		else:
			return True

	def processCommand(self, command):
		words = command.split('#')
		options = parseOptions(words)
		if words[0] == "connect":
			try:
				return self.connect(words[1])
			except:
				message = "ERROR" + '#' + 'Unexpected error while connecting to database'
				return message
		elif words[0] == "create":
			try:
				return self.create(words[1])
			except:
				message = "ERROR" + '#' + 'Unexpected error while creating od database'
				return message
		elif command == "save":
			return self.save()
		elif words[0] == "undo" and words[1] == "changes":
			return self.undoChanges()
		elif len(words) >= 2 and words[0] == "add" and words[1] == "unit":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				id = self.insertUnit(Unit(options["n"]))
				message = "INFO" + '#' + "Create unit. Id: " + str(id)
				return message
			except:
				message = "ERROR" + '#' + "Failed to add unit. Help:"
				return message
		elif len(words) >= 2 and words[0] == "add" and words[1] == "employee":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				unitId = int(options["u"])
				if not self.checkUnit(unitId):
					message = "ERROR" + '#' + "Incorrect unit id"
					return message
				id = self.insertEmployee(Employee(unitId, options["n"], int(options["r"]), int(options["e"])))
				message = "INFO" + '#' + "Create employee. Id: " + str(id)
				return message
			except:
				message = "ERROR" + '#' + "Failed to add employee"
				return message
		elif len(words) >= 2 and words[0] == "update" and words[1] == "unit":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				id = words[2]
				self.updateUnit(id, options)
				message = "INFO" + '#' + "Update unit " + str(id)
				return message
			except:
				message = "ERROR" + '#' + "Failed to update unit"
				return message
		elif len(words) >= 2 and words[0] == "update" and words[1] == "employee":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				if "u" in options:
					unitId = int(options["u"])
					if not self.checkUnit(unitId):
						message = "ERROR" + '#' + "Incorrect unit id"
						return message
				id = words[2]
				self.updateEmployee(id, options)
				message = "INFO" + '#' + "Update employee " + str(id)
				return message
			except:
				message = "ERROR" + '#' + "Failed to update employee"
				return message
		elif len(words) >= 2 and words[0] == "delete" and words[1] == "unit":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				id = words[2]
				self.deleteUnit(id)
				message = "INFO" + '#' + "Delete unit " + id
				return message
			except:
				message = "ERROR" + '#' + "Failed to delete unit"
				return message
		elif len(words) >= 2 and words[0] == "delete" and words[1] == "employee":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			try:
				id = words[2]
				self.deleteEmployee(id)
				message = "INFO" + '#' + "Delete employee " + id
				return message
			except:
				message = "ERROR" + '#' + "Failed to delete employee"
				return message
		elif len(words) >= 2 and words[0] == "select" and words[1] == "units":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			return self.selectUnits(options)
		elif len(words) >= 2 and words[0] == "select" and words[1] == "employees":
			if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
			return self.selectEmployees(options)
		elif words[0] == "stat":
			try:
				if self.__state == State.EMPTY: return "ERROR" + '#' + "not connected to database"
				if "-u" in words:
					return self.statU()
				elif "-r" in words:
					return self.statR()
				elif "-e" in words:
					return self.statE()
			except:
				message = "ERROR" + '#' + "Failed to print statistics"
				return message
		else:
			message = "ERROR" + '#' + "Unknown command"
			return message