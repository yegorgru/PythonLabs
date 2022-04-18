def parseOptions(args):
	options = dict()
	for arg in args:
		if arg.startswith('-'):
			options[arg[1]] = arg[2:]
	return options