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

	def statU(self, networkConn):
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
		networkConn.send(message.encode())

	def statR(self, networkConn):
		self.__cur.execute('''SELECT ID, NAME, RANK
			FROM Employee
			ORDER BY RANK DESC
			''')
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "Employee id: " + str(value[0]) + " name: " + value[1] + " rank: " + str(value[2])
		message = "TEXT" + '#' + output
		networkConn.send(message.encode())

	def statE(self, networkConn):
		self.__cur.execute('''SELECT ID, NAME, EXPERIENCE
			FROM Employee
			ORDER BY EXPERIENCE DESC
			''')
		output = ""
		for value in self.__cur.fetchall():
			if output != "": output = output + '\n'
			output = output + "Employee id: " + str(value[0]) + " name: " + value[1] + " experience: " + str(value[2])
		message = "TEXT" + '#' + output
		networkConn.send(message.encode())

	def checkEmpty(self, networkConn):
		if self.__state == State.EMPTY:
			message = "ERROR" + '#' + "not connected to database"
			networkConn.send(message.encode())
			return False;
		return True

	def __clean(self):
		self.__setState(State.EMPTY)
		if self.__currentFile != "":
			self.__conn.close()
		self.__setCurrentFile("")

	def save(self, networkConn):
		if not self.checkEmpty(networkConn): return
		self.__conn.commit()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "data saved"
		networkConn.send(message.encode())

	def undoChanges(self, networkConn):
		if not self.checkEmpty(networkConn): return
		self.__conn.rollback()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "data rolled back"
		networkConn.send(message.encode())

	def connect(self, file, networkConn):
		self.__clean()
		if not os.path.isfile(file):
			message = "ERROR" + '#' + "incorrect path"
			networkConn.send(message.encode())
			return;
		self.__setCurrentFile(file)
		self.__conn = sqlite3.connect(file)
		self.__cur = self.__conn.cursor()
		self.__setState(State.SAVED_CHANGES)
		message = "INFO" + '#' + "connected to " + file
		networkConn.send(message.encode())

	def create(self, file, networkConn):
		if file == "":
			message = "ERROR" + '#' + "empty file name"
			networkConn.send(message.encode())
			return;
		elif os.path.isfile(file):
			message = "ERROR" + '#' + "file already exists"
			networkConn.send(message.encode())
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
		self.connect(file, networkConn)

	def selectEmployees(self, options, networkConn):
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
		networkConn.send(message.encode())

	def selectUnits(self, options, networkConn):
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
		networkConn.send(message.encode())

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

	def processCommand(self, command, networkConn):
		words = command.split('#')
		options = parseOptions(words)
		if words[0] == "connect":
			try:
				self.connect(words[1], networkConn)
			except:
				message = "ERROR" + '#' + 'Unexpected error while connecting to database'
				networkConn.send(message.encode())
		elif words[0] == "create":
			try:
				self.create(words[1], networkConn)
			except:
				message = "ERROR" + '#' + 'Unexpected error while creating od database'
				networkConn.send(message.encode())
		elif command == "save":
			self.save(networkConn)
		elif words[0] == "undo" and words[1] == "changes":
			self.undoChanges(networkConn)
		elif len(words) >= 2 and words[0] == "add" and words[1] == "unit":
			if not self.checkEmpty(networkConn): return
			try:
				id = self.insertUnit(Unit(options["n"]))
				message = "INFO" + '#' + "Create unit. Id: " + str(id)
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to add unit. Help:"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "add" and words[1] == "employee":
			if not self.checkEmpty(networkConn): return
			try:
				unitId = int(options["u"])
				if not self.checkUnit(unitId):
					message = "ERROR" + '#' + "Incorrect unit id"
					networkConn.send(message.encode())
					return
				id = self.insertEmployee(Employee(unitId, options["n"], int(options["r"]), int(options["e"])))
				message = "INFO" + '#' + "Create employee. Id: " + str(id)
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to add employee"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "update" and words[1] == "unit":
			if not self.checkEmpty(networkConn): return
			try:
				id = words[2]
				self.updateUnit(id, options)
				message = "INFO" + '#' + "Update unit " + str(id)
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to update unit"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "update" and words[1] == "employee":
			if not self.checkEmpty(networkConn): return
			try:
				if "u" in options:
					unitId = int(options["u"])
					if not self.checkUnit(unitId):
						message = "ERROR" + '#' + "Incorrect unit id"
						networkConn.send(message.encode())
						return
				id = words[2]
				self.updateEmployee(id, options)
				message = "INFO" + '#' + "Update employee " + str(id)
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to update employee"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "delete" and words[1] == "unit":
			if not self.checkEmpty(networkConn): return
			try:
				id = words[2]
				self.deleteUnit(id)
				message = "INFO" + '#' + "Delete unit " + id
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to delete unit"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "delete" and words[1] == "employee":
			if not self.checkEmpty(networkConn): return
			try:
				id = words[2]
				self.deleteEmployee(id)
				message = "INFO" + '#' + "Delete employee " + id
				networkConn.send(message.encode())
			except:
				message = "ERROR" + '#' + "Failed to delete employee"
				networkConn.send(message.encode())
		elif len(words) >= 2 and words[0] == "select" and words[1] == "units":
			if not self.checkEmpty(networkConn): return
			self.selectUnits(options, networkConn)
		elif len(words) >= 2 and words[0] == "select" and words[1] == "employees":
			if not self.checkEmpty(networkConn): return
			self.selectEmployees(options, networkConn)
		elif words[0] == "stat":
			try:
				if not self.checkEmpty(networkConn): return
				if "-u" in words:
					self.statU(networkConn)
				elif "-r" in words:
					self.statR(networkConn)
				elif "-e" in words:
					self.statE(networkConn)
			except:
				message = "ERROR" + '#' + "Failed to print statistics"
				networkConn.send(message.encode())
		else:
			message = "ERROR" + '#' + "Unknown command"
			networkConn.send(message.encode())