#!/usr/bin/env python
# example_consumer.py
import pika, time
from configparser import ConfigParser
from subprocess import Popen, PIPE

def mbtiles_process_function(msg):
    print(" MBTiles processing")
    print(" [x] Received  %r" % str(msg, 'utf-8'))

    storm = str(msg, 'utf-8').split(' ')[-1]
    gdal2mbtiles_cmd = '/home/mbtiles/repos/gdal2mbtiles/gdal2mbtiles.py'
    tiff = '/home/mbtiles/storage/tiff/'+storm+'/maxele.63.tif'
    mbtiles_z0z9 = '/home/mbtiles/storage/mbtile/'+storm+'/maxele63-z0z9.mbtiles'
    mbtiles_z10 = '/home/mbtiles/storage/mbtile/'+storm+'/maxele63-z10.mbtiles'
    mbtiles_z11 = '/home/mbtiles/storage/mbtile/'+storm+'/maxele63-z11.mbtiles'
    mbtiles_z12 = '/home/mbtiles/storage/mbtile/'+storm+'/maxele63-z12.mbtiles'

    cmds_list = [
      ['python', gdal2mbtiles_cmd, tiff, '-z', '0-9', '--processes=2', mbtiles_z0z9],
      ['python', gdal2mbtiles_cmd, tiff, '-z', '10', '--processes=2', mbtiles_z10],
      ['python', gdal2mbtiles_cmd, tiff, '-z', '11', '--processes=3', mbtiles_z11],
      ['python', gdal2mbtiles_cmd, tiff, '-z', '12', '--processes=4', mbtiles_z12]
    ]
    procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]

    for proc in procs_list:
        proc.wait()

    time.sleep(msg.count(b'.')) # delays for 5 seconds
    print(" MBTiles processing for "+storm+" finished")
    return

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
print(' [*] Waiting for messages. To exit press CTRL+C')

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  mbtiles_process_function(body)
  ch.basic_ack(delivery_tag=method.delivery_tag)

# set up subscription on the queue
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='mbtilesprocess', on_message_callback=callback)

# start consuming (blocks)
channel.start_consuming()

# close channel and connection
channel.close()
connection.close()
