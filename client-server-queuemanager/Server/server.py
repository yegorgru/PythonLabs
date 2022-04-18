from hr import HumanResourcesManager

import pika
	

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='server_queue')
channel.queue_declare(queue='client_queue')
manager = HumanResourcesManager()
print('Server started...')

def callback(ch, method, properties, body):
	print('Receive query', body.decode())
	response = manager.processCommand(body.decode())
	channel.basic_publish(exchange='', routing_key='client_queue', body=response)

try:
	channel.basic_consume(queue='server_queue', on_message_callback=callback, auto_ack=True)
	channel.start_consuming()
except KeyboardInterrupt:
	print('Server stopped')
	connection.close()