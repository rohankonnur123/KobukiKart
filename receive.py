#!/usr/bin/env python
import pika
import lightsensor_pb2
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
channel = connection.channel()
channel.queue_declare(queue='hello')
lightsensor = lightsensor_pb2.LightSensor()

def callback(ch, method, properties, body):
    lightsensor.ParseFromString(body)
    print(" [x] Received\n" + str(lightsensor))

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
