class Employee:
	def __init__(self, unitId, name, rank, experience):
		self.setUnitId(unitId)
		self.setName(name)
		self.setRank(rank)
		self.setExperience(experience)

	def getName(self):
		return self.__name

	def setName(self, value):
		self.__name = value

	def getRank(self):
		return self.__rank

	def setRank(self, value):
		self.__rank = value

	def getExperience(self):
		return self.__experience

	def setExperience(self, value):
		self.__experience = value

	def getUnitId(self):
		return self.__unitId

	def setUnitId(self, value):
		self.__unitId = value