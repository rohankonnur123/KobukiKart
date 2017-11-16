#!/usr/bin/env python
import pika
import lightsensor_pb2
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
channel = connection.channel()

def PromptForLightSensor(lightsensor):
  lightsensor.leftBump = bool(raw_input("Enter leftBump (blank for False): "))
  lightsensor.centerBump = bool(raw_input("Enter centerBump (blank for False): "))
  lightsensor.rightBump = bool(raw_input("Enter rightBump (blank for False): "))
  lightsensor.banana = bool(raw_input("Enter banana (blank for False): "))
  lightsensor.mushroom = bool(raw_input("Enter mushroom (blank for False): "))

lightsensor = lightsensor_pb2.LightSensor()

channel.queue_declare(queue='hello')

while True:
  PromptForLightSensor(lightsensor)
  channel.basic_publish(exchange='',
                        routing_key='hello',
                        body=str(lightsensor.SerializeToString()))
  print(" [x] Sent\n" + str(lightsensor))
connection.close()
