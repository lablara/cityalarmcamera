# *********************************************************************
# This class receives an EA and send it to the requesting EAC
# It is implemented to communicate through the MQTT protocol
# A MQTT Broker is required - We recommend the Mosquitto implementation (https://mosquitto.org)
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 2020/05/12
# *********************************************************************

import paho.mqtt.client as mqtt
from time import sleep
import sys

########################################################

class epuMQTT():
    def __init__(self, ipBroker, epuId):
        self.broker = ipBroker
        self.description = "EPU_CityAlarmCamera_" + str(epuId)

        # MQTT client object is created
        self.clientmqtt = mqtt.Client("")

    def publishEA (self, eaJSON):
        try:
            self.clientmqtt.connect(self.broker)

            print("Publishing an Emergency Alarm (EA) to the MQTT Broker: ", self.broker)
        
            # Associating a "topic" to a "payload"
            self.clientmqtt.publish (self.description, eaJSON)

            sleep(1)
            
            # Disconnecting
            self.clientmqtt.disconnect()
            
            print("The Emergency Alarm was published!")

        except:
            print("Connection to the MQTT Broker has failed. Address: ", self.broker, ". EPU is exiting...")
            sys.exit(1)
