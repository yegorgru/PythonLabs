from colorama import init, Fore

init(autoreset=True)

class Logger:
	def __init__(self, isDebug):
		if type(isDebug) != bool:
			ERROR("Failed to set debug mode")
			exit()
		self.__isDebug = isDebug
		

	def INFO(self, message):
		print(Fore.GREEN + message)

	def ERROR(self, message):
		print(Fore.RED + message)

	def WARNING(self, message):
		print(Fore.CYAN + message)

	def DEBUG(self, message):
		if self.__isDebug:
			print(Fore.YELLOW + message)