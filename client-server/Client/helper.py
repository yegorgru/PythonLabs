class Helper:
	def __init__(self, helpDictionary):
		if type(helpDictionary) != dict:
			ERROR()
		self.__helpDictionary = helpDictionary

	def printHelpCommand(self, key):
		if type(self.__helpDictionary[key]) == str:
			print("\t", key, " - ", self.__helpDictionary[key])
		else:
			print("\t", key, " - ", self.__helpDictionary[key][0])
			print("\t\tOptions:")
			nestedDict = self.__helpDictionary[key][1]
			for nestedKey in nestedDict:
				print("\t\t", nestedKey, " - ", nestedDict[nestedKey])

	def printHelpInfo(self):
		for key in self.__helpDictionary:
			self.printHelpCommand(key)