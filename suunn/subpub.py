# The MIT License (MIT)
#Adapted from
# Copyright (c) 2019 Mike Teachman
# https://opensource.org/licenses/MIT
#
# Example MicroPython and CircuitPython code showing how to use the MQTT protocol with Adafruit IO, to  
# publish and subscribe on the same device
  

import network
import time
from umqtt.robust import MQTTClient
import os
import gc
import sys
from machine import Pin
import neopixel



    
##########################################################
NEO_PIN = 26
LIGHTS = 24
np = neopixel.NeoPixel(Pin(NEO_PIN), LIGHTS) #using 24 pixel ring

# the following function is the callback which is 
# called when subscribed data is received
def cb(topic, msg):
    """"""
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    color = msg.decode("utf-8")
    color = str(color.replace('#',''))
    
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6],16)
    print("green: ", g)
    for i in range(LIGHTS):
        
        np[i] = (r,g,b)
    np.write()
    
# WiFi connection information
WIFI_SSID = "MiddleburyGuest"
WIFI_PASSWORD = ""


wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID , WIFI_PASSWORD)
wifi.isconnected()
wifi.ifconfig()


# turn off the WiFi Access Point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# connect the device to the WiFi network
"""wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)"""

# wait until the device is connected to the WiFi network
MAX_ATTEMPTS = 20
attempt_count = 0
while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    time.sleep(1)

if attempt_count == MAX_ATTEMPTS:
    print('could not connect to the WiFi network')
    sys.exit()

# create a random MQTT clientID 
random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id = bytes('client_'+str(random_num), 'utf-8')

# connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
# 
# To use a secure connection (encrypted) with TLS: 
#   set MQTTClient initializer parameter to "ssl=True"
#   Caveat: a secure connection uses about 9k bytes of the heap
#         (about 1/4 of the micropython heap on the ESP8266 platform)
ADAFRUIT_IO_URL = b'io.adafruit.com'
ADAFRUIT_USERNAME = b'daninewbs'
ADAFRUIT_IO_KEY = b'aio_bCEI63Fos0raJdEpQB3mt6w47DqU'
ADAFRUIT_IO_FEEDNAME_PUB = b'esp32mem'
ADAFRUIT_IO_FEEDNAME_SUB = b'color-picker'
client = MQTTClient(client_id=mqtt_client_id,
                    server=ADAFRUIT_IO_URL,
                    user=ADAFRUIT_USERNAME,
                    password=ADAFRUIT_IO_KEY,
                    ssl=True)
try:
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()

                    

        

mqtt_feedname_pub = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME_PUB), 'utf-8')
mqtt_feedname_sub = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME_SUB), 'utf-8')

client.set_callback(cb)
client.subscribe(mqtt_feedname_sub)

# wait until data has been Published to the Adafruit IO feed
while True:
    try:
        client.wait_msg()  # Blocking: sits here until a message is received
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()

