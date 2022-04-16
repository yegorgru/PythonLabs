import logger

class Employee:
	def __init__(self, unitId, name, rank, experience):
		self.setUnitId(unitId)
		self.setName(name)
		self.setRank(rank)
		self.setExperience(experience)

	def getName(self):
		return self.__name

	def setName(self, value):
		if type(value) != str:
			ERROR('name must be str')
			exit()
		self.__name = value

	def getRank(self):
		return self.__rank

	def setRank(self, value):
		if type(value) != int:
			ERROR('rank must be int')
			exit()
		self.__rank = value

	def getExperience(self):
		return self.__experience

	def setExperience(self, value):
		if type(value) != int:
			ERROR('experience must be int')
			exit()
		self.__experience = value

	def getUnitId(self):
		return self.__unitId

	def setUnitId(self, value):
		if type(value) != int:
			ERROR('unitId must be int')
			exit()
		self.__unitId = value