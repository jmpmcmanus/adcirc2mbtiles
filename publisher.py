#!/usr/bin/env python
# publisher.py
import pika, logging, sys
from configparser import ConfigParser

# set up logging
logging.basicConfig()

# retrieve configuration settings
parser = ConfigParser()
parser.read('/srv/mbtiles/config.ini')

# set up AMQP credentials and connect to asgs queue
credentials = pika.PlainCredentials(parser.get('pika', 'username'),
                                            parser.get('pika', 'password'))
parameters = pika.ConnectionParameters(parser.get('pika', 'host'),
                                       parser.get('pika', 'port'),
                                       '/',
                                       credentials,
                                       socket_timeout=2)

# Connect
connection = pika.BlockingConnection(parameters)
channel = connection.channel() # start a channel
channel.queue_declare(queue='mbtilesprocess', durable=True) # Declare a queue

# send a message
message = ' '.join(sys.argv[1:]) or "Start Processing MBTiles for florence"
channel.basic_publish(exchange='', routing_key='mbtilesprocess', body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    )
)
print ("[x] Message sent to consumer")
connection.close()

