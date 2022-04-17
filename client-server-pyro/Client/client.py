from helper import Helper
from logger import Logger
from enum import Enum

import Pyro4
import sys

class Code(Enum):
	INFO = 0,
	WARNING = 1,
	ERROR = 2,
	TEXT = 3

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

if "-d" in sys.argv:
	logger = Logger(True)
else:
	logger = Logger(False)
#try:
ns = Pyro4.locateNS()
uri = ns.lookup('manager')
manager = Pyro4.Proxy(uri)
while True:
	command = input()
	words = command.split()
	if command == "":
		continue
	elif command == "q":
		break
	elif command == "help":
		helper.printHelpInfo()
		continue
	elif words[0] == "connect":
		if len(words) != 2:
			logger.ERROR("Incorrect use of connect. Help:")
			helper.printHelpCommand("connect [FILE]")
			continue
	elif words[0] == "create":
		if len(words) != 2:
			logger.ERROR("Incorrect use of create. Help:")
			helper.printHelpCommand("create [FILE]")
			continue
	elif len(words) >= 2 and words[0] == "update" and words[1] == "unit":
		if len(words) < 3:
			logger.ERROR("Incorrect use of update unit. Help:")
			helper.printHelpCommand("update unit [UNIT ID]")
			continue
	elif len(words) >= 2 and words[0] == "update" and words[1] == "employee":
		if len(words) < 3:
			logger.ERROR("Incorrect use of update employee. Help:")
			helper.printHelpCommand("update employee [EMPLOYEE ID]")
			continue
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "unit":
		if len(words) != 3:
			logger.ERROR("Incorrect use of delete unit. Help:")
			helper.printHelpCommand("delete unit [UNIT_ID]")
			continue
	elif len(words) >= 2 and words[0] == "delete" and words[1] == "employee":
		if len(words) != 3:
			logger.ERROR("Incorrect use of delete employee. Help:")
			helper.printHelpCommand("delete employee [EMPLOYEE_ID]")
			continue
	query = ""
	for word in words:
		if query != "": query = query + '#'
		query = query + word
	result = manager.processCommand(query).split('#')
	code = Code[result[0]]
	if code == Code.ERROR:
		logger.ERROR(result[1])
	elif code == Code.INFO:
		logger.INFO(result[1])
	elif code == Code.WARNING:
		logger.WARNING(result[1])
	elif code == Code.TEXT:
		print(result[1])
#except:
#	print("Disconnected from server")