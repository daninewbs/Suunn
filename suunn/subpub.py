# The MIT License (MIT)
# Adapted from
# Copyright (c) 2019 Mike Teachman
# https://opensource.org/licenses/MIT
#
# Example MicroPython and CircuitPython code showing how to use the MQTT protocol with Adafruit IO, to
# publish and subscribe on the same device

import network
import json
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
np = neopixel.NeoPixel(Pin(NEO_PIN), LIGHTS)  # using 24 pixel ring


CACERT_PATH = "../ESP_SECRETS/AmazonRootCA1.pem"
KEY_PATH = "../ESP_SECRETS/private.pem.key"
CERT_PATH = "../ESP_SECRETS/certificate.pem.crt"
with open(KEY_PATH, "r") as f:
    key1 = f.read()

with open(CACERT_PATH, "r") as f:
    key2 = f.read()

with open(CERT_PATH, "r") as f:
    cert1 = f.read()

print(cert1)


class MQTT:
    def __init__(self) -> None:
        # MQTT SETUP
        # WiFi connection information
        WIFI_SSID = "Storm"
        WIFI_PASSWORD = "!Onward!"

        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
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
            print("could not connect to the WiFi network")
            sys.exit()

        # create a random MQTT clientID
        random_num = int.from_bytes(os.urandom(3), "little")
        mqtt_client_id = bytes("client_" + str(random_num), "utf-8")

        # connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
        #
        # To use a secure connection (encrypted) with TLS:
        #   set MQTTClient initializer parameter to "ssl=True"
        #   Caveat: a secure connection uses about 9k bytes of the heap
        #         (about 1/4 of the micropython heap on the ESP8266 platform)

        AWS_HOSTNAME = b"a5lu8ppnce8yt-ats.iot.us-west-2.amazonaws.com"

        ADAFRUIT_IO_FEEDNAME_PUB = b"esp32mem"
        ADAFRUIT_IO_FEEDNAME_SUB = b"color-picker"
        self.client = MQTTClient(
            client_id=mqtt_client_id,
            server=AWS_HOSTNAME,
            port=8883,
            ssl=True,
            ssl_params={"key": key1, "cert": cert1},
        )

        try:
            self.client.connect()
        except Exception as e:
            print("could not connect to MQTT server {}{}".format(type(e).__name__, e))
            sys.exit()

        # mqtt_feedname_pub = bytes(
        #     "{:s}/feeds/{:s}".format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME_PUB),
        #     "utf-8",
        # )
        # mqtt_feedname_sub = bytes(
        #     "{:s}/feeds/{:s}".format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME_SUB),
        #     "utf-8",
        # )

        self.client.set_callback(self.cb)
        self.client.subscribe(bytes("suunn/color", "utf-8"))

    # the following function is the callback which is
    # called when subscribed data is received
    def cb(self, topic, msg):
        """"""
        print("Received Data:  Topic = {}, Msg = {}".format(topic, msg))
        message = json.loads(msg.decode("utf-8"))
        if topic.decode("utf-8") == "suunn/color":
            color = message.get("color", "#FFFFF")
            color = str(color.replace("#", ""))

            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            for i in range(LIGHTS):

                np[i] = (r, g, b)
            np.write()

