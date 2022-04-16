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