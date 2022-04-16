import logger

class Unit:
	def __init__(self, name):
		self.__employees = set()
		self.setName(name)

	def getName(self):
		return self.__name

	def setName(self, value):
		if type(value) != str:
			ERROR('name must be str')
			exit()
		self.__name = value

	def getEmployees(self):
		return self.__employees

	def setEmployees(self, value):
		if type(value) != set:
			ERROR('employees must be set')
			exit()
		self.__employees = value