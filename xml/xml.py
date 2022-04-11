from lxml import etree as ET
import colorama
from colorama import init, Fore
from enum import Enum
import os.path
import sys
from io import StringIO

init(autoreset=True)

helpDict = {
    "help": "print help info",
    "new [FILE]": "create xml file",
    "load [FILE]": "load xml file",
    "save": ("save file", {"-f[FILE]": "save to specified file"}),
    "add unit": ("add new unit", {"-n[NAME]": "unit name"}),
    "add employee": ("add new employee", {"-n[NAME]": "employee name", "-u[ID]": "unit id", "-r[RANK]": "employee's rank", "-e[EXPERIENCE]": "employee's experience"}),
    "update unit [UNIT ID]": ("update unit info", {"-n[NAME]": "update name"}),
    "update employee [EMPLOYEE ID]": ("update employee's info", {"-n[NAME]": "update name", "-u[ID]": "update unit id", "-r[RANK]": "update rank", "-e[EXPERIENCE]": "update experience"}),
    "delete unit [UNIT_ID]": "delete unit",
    "delete employee [EMPLOYEE_ID]": "delete employee",
    "info unit [UNIT_ID]": "print unit info",
    "info employee [EMPLOYEE_ID]": "print employee info",
    "all units": "print all valid unit ids",
    "all employees": "print all valid employee ids",
    "stat": ("print statistics", {"-u": "print units order by number of employees", "-r": "print employees order by rank", "-e": "print employees order by experience"}),
    "q": "exit"
}

def printHelpCommand(key):
	if type(helpDict[key]) == str:
		print("\t", key, " - ", helpDict[key])
	else:
		print("\t", key, " - ", helpDict[key][0])
		print("\t\tOptions:")
		nestedDict = helpDict[key][1]
		for nestedKey in nestedDict:
			print("\t\t", nestedKey, " - ", nestedDict[nestedKey])

def printHelpInfo():
	for key in helpDict:
		printHelpCommand(key)

def INFO(message):
	print(Fore.GREEN + message)

def ERROR(message):
	print(Fore.RED + message)

def WARNING(message):
	print(Fore.CYAN + message)

def DEBUG(message):
	if isDebug:
		print(Fore.YELLOW + message)

def yesNoDialog():
	while True:
		answer = input()
		if answer == "y": return True
		elif answer == "n": return False
		else: print("Please, answer y or n") 

def parseOptions(args):
	options = dict()
	for arg in args:
		if arg.startswith('-'):
			options[arg[1]] = arg[2:]
	return options

class State(Enum):
	EMPTY = 0,
	UNSAVED_CHANGES = 1,
	SAVED_CHANGES = 2

class Employee:
	def __init__(self, unitId, name, rank, experience):
		self.mUnitId = unitId
		self.mName = name
		self.mRank = rank
		self.mExperience = experience

class Unit:
	def __init__(self, name):
		self.mEmployees = set()
		self.mName = name

class HumanResourcesManager:
	def __init__(self):
		self.mUnits = dict()
		self.mEmployees = dict()
		self.mState = State.EMPTY
		self.mCurrentFile = ""

	def createEmployee(self, employee):
		if len(self.mEmployees) == 0:
			key = 0;
		else:
			key = max(self.mEmployees.keys()) + 1
		self.mEmployees[key] = employee 
		self.mUnits[employee.mUnitId].mEmployees.add(key)
		return key

	def createUnit(self, unit):
		if len(self.mUnits) == 0:
			key = 0;
		else:
			key = max(self.mUnits.keys()) + 1
		self.mUnits[key] = unit
		return key 

	def statU(self):
		items = list(self.mUnits.items())
		items.sort(key=lambda x: len(x[1].mEmployees), reverse=True)
		for key, value in items:
			print("Unit id: ", key, ", name: ", value.mName, ", number of employees: ", len(value.mEmployees))

	def statR(self):
		items = list(self.mEmployees.items())
		items.sort(key=lambda x: x[1].mRank, reverse=True)
		for key, value in items:
			print("Employee id: ", key, ", name: ", value.mName, ", rank: ", value.mRank)

	def statE(self):
		items = list(self.mEmployees.items())
		items.sort(key=lambda x: x[1].mExperience, reverse=True)
		for key, value in items:
			print("Employee id: ", key, ", name: ", value.mName, ", experience: ", value.mExperience)

	def checkEmpty(self):
		if self.mState == State.EMPTY:
			ERROR("document is not loaded")
			return False;
		return True

	def suggestSave(self):
		if self.mState == State.UNSAVED_CHANGES:
			WARNING("You have unsaved changes, save it? [y/n]")
			answer = yesNoDialog()
			if answer:
				self.save(self.mCurrentFile)

	def clean(self):
		self.mUnits = dict()
		self.mEmployees = dict()
		self.mState = State.EMPTY
		self.mCurrentFile = ""

	def save(self, file):
		if not self.checkEmpty(): return
		root = ET.Element('company')
		tree = ET.ElementTree(root)
		units = ET.SubElement(root, "units")
		for key, value in self.mUnits.items():
			unit = ET.SubElement(units, "unit")
			unit.set("id", str(key))
			name = ET.SubElement(unit, "unitName")
			name.text = value.mName
			unitEmployees = ET.SubElement(unit, "unitEmployees")
			for employee in value.mEmployees:
				unitEmployee = ET.SubElement(unitEmployees, "unitEmployee")
				unitEmployee.set("id", str(employee))
		employees = ET.SubElement(root, "employees")
		for key, value in self.mEmployees.items():
			employee = ET.SubElement(employees, "employee")
			employee.set("id", str(key))
			name = ET.SubElement(employee, "name")
			name.text = value.mName
			unitId = ET.SubElement(employee, "unitId")
			unitId.text = str(value.mUnitId)
			rank = ET.SubElement(employee, "rank")
			rank.text = str(value.mRank)
			experience = ET.SubElement(employee, "experience")
			experience.text = str(value.mExperience)
		with open(file, 'wb') as f:
			tree.write(f, pretty_print=True, encoding='utf-8')
		if  self.mCurrentFile == file:
			self.mState = State.SAVED_CHANGES
		INFO(file + " saved")

	def load(self, file):
		self.suggestSave()
		self.clean()
		if not os.path.isfile(file):
			ERROR("incorrect path")
			return;
		f = open(file, "r")
		try:
			xmlDoc = ET.fromstring(f.read())
			dtd = ET.DTD(open(dtdPath))
			if not dtd.validate(xmlDoc):
				ERROR("Dtd validation not passed")
				return
		except:
			ERROR("Error while parsing. Invalid document")
			return
		for xmlUnit in xmlDoc.findall("units/unit"):
			id = int(xmlUnit.get('id'))
			name = xmlUnit.find('unitName').text
			unit = Unit(name)
			self.mUnits[id] = unit
			DEBUG("Parse unit. Id: " + str(id) + ", name: " + name)
			for xmlUnitEmployee in xmlUnit.findall("unitEmployees/unitEmployee"):
				employeeId = int(xmlUnitEmployee.get('id'))
				DEBUG("Parse employee in unit. Id: " + str(employeeId))
				self.mUnits[id].mEmployees.add(employeeId)
		for xmlEmployee in xmlDoc.findall("employees/employee"):
			id = int(xmlEmployee.get('id'))
			unitId = int(xmlEmployee.find('unitId').text)
			name = xmlEmployee.find('name').text
			rank = int(xmlEmployee.find('rank').text)
			experience = int(xmlEmployee.find('experience').text)
			DEBUG("Parse employee. Id: " + str(id) + ", unitId: " + str(unitId) + ", name: " + name + ", rank: " + str(rank) + ", experience: " + str(experience))
			employee = Employee(unitId, name, rank, experience)
			self.mEmployees[id] = employee
		loadedEmployees = [];
		for key, value in self.mUnits.items():
			for employee in value.mEmployees:
				if not employee in self.mEmployees:
					ERROR("Unexisting employee in unit " + value.mName)
					self.clean()
					continue
				if self.mEmployees[employee].mUnitId != key:
					ERROR("Unexpected unitId of employee " + employee)
					self.clean()
					continue
				loadedEmployees.append(employee)
		for key in self.mEmployees:
			if not key in loadedEmployees:
				ERROR("Unexpected employee " + key)
				self.clean()
				continue
		INFO(file + " loaded. " + str(len(self.mUnits)) + " units, " + str(len(self.mEmployees)) + " employees.")
		self.mState = State.SAVED_CHANGES
		self.mCurrentFile = file

	def new(self, file):
		if os.path.isfile(file):
			ERROR("File already exists")
		else:
			root = ET.Element('company')
			tree = ET.ElementTree(root)
			units = ET.SubElement(root, "units")
			employees = ET.SubElement(root, "employees")
			with open(file, 'wb') as f:
				tree.write(f, pretty_print=True, encoding='utf-8')
			self.load(file)

opts = parseOptions(sys.argv)
if "d" in opts:
	isDebug = True;
else:
	isDebug = False;
dtdPath = opts.get("s", "schema.dtd")
DEBUG("Dtd path: " + dtdPath)
manager = HumanResourcesManager()
while True:
	if(manager.mCurrentFile != ""):
		hint = "[" + manager.mCurrentFile + "]: "
	else:
		hint = ""
	command = input(hint)
	words = command.split()
	if command == "q":
		manager.suggestSave()
		exit()
	elif command == "help":
		printHelpInfo()
	elif words[0] == "load":
		if len(words) != 2:
			ERROR("Incorrect use of load. Help:")
			printHelpCommand("load [FILE]")
		else:
			manager.load(words[1])
	elif words[0] == "new":
		words = command.split()
		if len(words) != 2:
			ERROR("Incorrect use of new. Help:")
			printHelpCommand("new [FILE]")
		else:
			manager.new(words[1])
	elif words[0] == "save":
		words = command.split()
		options = parseOptions(words)
		file = options.get("f", manager.mCurrentFile)
		DEBUG("save to file " + file)
		manager.save(file)
	elif len(words) >= 2 and words[0] == "add" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		options = parseOptions(command.split())
		try:
			id = manager.createUnit(Unit(options["n"]))
			INFO("Create unit. Id: " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to add unit. Help:")
			printHelpCommand("add unit")
	elif len(words) >= 2 and words[0] == "add" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		options = parseOptions(command.split())
		try:
			unitId = int(options["u"])
			if not unitId in manager.mUnits:
				ERROR("Incorrect unit id")
				continue
			id = manager.createEmployee(Employee(unitId, options["n"], int(options["r"]), int(options["e"])))
			INFO("Create employee. Id: " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to add employee. Help:")
			printHelpCommand("add employee")
	elif len(words) >= 2 and words[0] == "update" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		words = command.split()
		options = parseOptions(words)
		if len(words) < 3:
			ERROR("Incorrect use of update unit. Help:")
			printHelpCommand("update unit [UNIT ID]")
			continue;
		try:
			id = int(words[2])
			if not id in manager.mUnits:
				ERROR("Incorrect id")
				continue;
			if "n" in options:
				manager.mUnits[id].mName = options["n"]
			INFO("Update unit " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to update unit. Help:")
			printHelpCommand("update unit [UNIT ID]")
	elif len(words) >= 2 and words[0] == "update" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		words = command.split()
		options = parseOptions(words)
		if len(words) < 3:
			ERROR("Incorrect use of update employee. Help:")
			printHelpCommand("update employee [EMPLOYEE ID]")
			continue;
		try:
			id = int(words[2])
			if not id in manager.mEmployees:
				ERROR("Incorrect id")
				continue;
			if "n" in options:
				manager.mEmployees[id].mName = options["n"]
			if "e" in options:
				manager.mEmployees[id].mExperience = int(options["e"])
			if "r" in options:
				manager.mEmployees[id].mRank = int(options["r"])
			if "u" in options:
				oldUnitId = manager.mEmployees[id].mUnitId
				newUnitId = int(options["u"])
				if not newUnitId in manager.mUnits:
					ERROR("Incorrect unit id specified")
				else:
					manager.mUnits[oldUnitId].mEmployees.remove(employeeId)
					manager.mUnits[newUnitId].mEmployees.add(employeeId)
					manager.mEmployees[id].mUnitId = newUnitId
			INFO("Update employee " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to update employee. Help:")
			printHelpCommand("update employee [EMPLOYEE ID]")
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			ERROR("Incorrect use of delete unit. Help:")
			printHelpCommand("delete unit [UNIT_ID]")
		try:
			id = int(words[2])
			if not id in manager.mUnits:
				ERROR("Incorect id")
				continue
			for employeeId in manager.mUnits[id].mEmployees:
				del manager.mEmployees[employeeId]
			del manager.mUnits[id]
			INFO("Delete unit " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to delete unit. Help:")
			printHelpCommand("delete unit [UNIT_ID]")
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			ERROR("Incorrect use of delete employee. Help:")
			printHelpCommand("delete employee [EMPLOYEE_ID]")
		try:
			id = int(words[2])
			if not id in manager.mEmployees:
				ERROR("Incorect id")
				continue
			manager.mUnits[manager.mEmployees[id].mUnitId].mEmployees.remove(id)
			del manager.mEmployees[id]
			INFO("Delete employee " + str(id))
			manager.mState = State.UNSAVED_CHANGES
		except:
			ERROR("Failed to delete employee. Help:")
			printHelpCommand("delete employee [EMPLOYEE_ID]")
	elif len(words) >= 2 and words[0] == "info" and words[1] == "unit":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			ERROR("Incorrect use of info unit. Help:")
			printHelpCommand("info unit [UNIT_ID]")
		try:
			id = int(words[2])
			if not id in manager.mUnits:
				ERROR("Incorect id")
				continue
			unit = manager.mUnits[id]
			print("Name: ", unit.mName)
			if len(unit.mEmployees) == 0:
				employeesStr = "No employees"
			else:
				employeesStr = "Employees:"
			for employeeId in unit.mEmployees:
				employeesStr = employeesStr + " " + str(employeeId)
			print(employeesStr)
		except:
			ERROR("Failed to print info about unit. Help:")
			printHelpCommand("info unit [UNIT_ID]")
	elif len(words) >= 2 and words[0] == "info" and words[1] == "employee":
		if not manager.checkEmpty(): continue
		if len(words) != 3:
			ERROR("Incorrect use of info employee. Help:")
			printHelpCommand("info employee [EMPLOYEE_ID]")
		try:
			id = int(words[2])
			if not id in manager.mEmployees:
				ERROR("Incorect id")
				continue
			employee = manager.mEmployees[id]
			print("Name: ", employee.mName)
			print("Unit: ", employee.mUnitId)
			print("Rank: ", employee.mRank)
			print("Experience: ", employee.mExperience)
		except:
			ERROR("Failed to print info about employee. Help:")
			printHelpCommand("info employee [EMPLOYEE_ID]")
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
			ERROR("Failed to print statistics. Help:")
			printHelpCommand("stat")
	elif len(words) == 2 and words[0] == "all" and words[1] == "units":
		if not manager.checkEmpty(): continue
		try:
			output = ""
			for key in manager.mUnits.keys():
				output = output + str(key) + " "
			print(output)
		except:
			ERROR("Failed to print all units. Help:")
			printHelpCommand("all units")
	elif len(words) == 2 and words[0] == "all" and words[1] == "employees":
		if not manager.checkEmpty(): continue
		try:
			output = ""
			for key in manager.mEmployees.keys():
				output = output + str(key) + " "
			print(output)
		except:
			ERROR("Failed to print all employees. Help:")
			printHelpCommand("all employees")
	else:
		ERROR("Unknown command")
