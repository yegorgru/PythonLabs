from hr import HumanResourcesManager

import Pyro4

daemon = Pyro4.Daemon()
uri = daemon.register(HumanResourcesManager)
ns = Pyro4.locateNS()
ns.register('manager', uri)
daemon.requestLoop()