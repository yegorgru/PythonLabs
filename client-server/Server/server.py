import socket
from enum import Enum

from hr import HumanResourcesManager
		

s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))

try:
	while True:
		s.listen()
		print('Waiting for a client')
		conn, addr = s.accept()
		print('Got connection from ', addr)
		manager = HumanResourcesManager()
		while True:
			command = conn.recv(1024).decode()
			if command == "q":
				break
			manager.processCommand(command, conn)
except KeyboardInterrupt:
	print("Server stopped")