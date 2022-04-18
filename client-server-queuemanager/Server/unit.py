class Unit:
	def __init__(self, name):
		self.__employees = set()
		self.setName(name)

	def getName(self):
		return self.__name

	def setName(self, value):
		self.__name = value

	def getEmployees(self):
		return self.__employees

	def setEmployees(self, value):
		self.__employees = value