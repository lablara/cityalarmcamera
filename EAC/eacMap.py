#!/usr/bin/env python3

# *********************************************************************
# This is an Emergency Alarm Client (EAC) that creates html maps plotting
# the occurrence of Emergency Alarms
# This implementation plots alarms considering the presence of instance and complex events
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date         : 12/05/2020
# *********************************************************************

import time
import sys, getopt
import atexit
import threading
import paho.mqtt.client as mqtt
import folium
import json

## Supporting classes
from elementsEAC import EA, GPS, ListEA

##############################################################################

## Constants and variables
debug = True
ipBroker = "192.168.1.100"  # The IP address of the MQTT Broker - can be provided as a command-line argument
requestEA = "EPU_CityAlarmCamera_1"  # MQTT subject to be subscribed to EPU1 - any EPU may be 

## Frequency to refresh the map
refreshTime = 60  # After 120s, Emergency Alarms that were not refreshed will be removed from the list of active EA

## List of all alarms
alarms = ListEA()

## Variables related to the creation of the Map
## This is the center of the city to be considered
mapGPS = GPS(41.14961,-8.61099)  # The center of Porto, Portugal
zoomSize = 13  # Configuraton for the folium library. This is the initial zooming of the map

## List of possible EI, as employed in the EDU
## The format is [type,threshold,symbol(1 for >= and 0 for <=),textual description]
possibleEI = [[1,60,1,"Heating"], \
              [2,-20,0,"Freezing"], \
              [3,10,0,"Humidty"], \
              [4,500,1,"Smoke"], \
              [5,35,1,"Gas"], \
              [6,10,1,"Rain"], \
              [7,6.5,1,"Earhquake"], \
              [8,50,1,"Noise"], \
              [9,300,1,"Radiation"], \
              [10,5,1,"BlastWave"], \
              [11,80,1,"Wind"], \
              [12,1,0,"Luminosity"], \
              [13,50,1,"Snowing"], \
              [14,95,1,"DamLevel"], \
              [15,600,1,"Pollution"], \
              [16,0,0,"Flooding"]]

## List of possible EC, as employed in the EDU
possibleEC = [[1,"Fire"], \
              [2,"Smoke"], \
              [3,"Fire and smoke"], \
              [4,"Car accident"], \
              [5,"Injured people"], \
              [6,"Explosion"], \
              [7,"Panic"]]

# In this implementation, only the complex event w = 1 (Fire) is being modelled

##############################################################################

### This thread is used to remove old EA from the list, when they are not being reported anymore
class mapRefresher (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global refreshTime, alarms, debug

        while True:
            time.sleep(refreshTime)

            if debug:
                print ("Updating list of received EA")

            ## Remove old EAs
            alarms.updateAlarms(refreshTime, debug)

            plotMap()

##############################################################################

## This function creates the HTML map according to the list of active EAs
def plotMap():
    global alarms, mapGPS, zoomSize, requestEA, possibleEI, possibleEC, debug

    ## Requesting block for the use of this method
    lock = threading.Lock()
    lock.acquire()
    
    ## Map to be created
    map = folium.Map(location=[mapGPS.la, mapGPS.lo], zoom_start=zoomSize, control_scale=True)

    ## Plot all alarms in the created map
    for ea in alarms.getAlarms():
        descriptions = ""
 
        # Instance events
        typesI = ea.getEventsInstanceTypes()
        if len(typesI) > 0:
            descriptions = "Instance:\n"
            for y in typesI:
                descriptions = descriptions + str(possibleEI[y-1][3]) + "\n"
            
        # Complex events
        typesC = ea.getEventsComplexTypes()
        if len(typesC) > 0:
            descriptions = descriptions + "Complex:\n"
            for y in typesC:
                descriptions = descriptions + str(possibleEC[y-1][1]) + "\n"
    
        #Different colors for the pins, according to the types of detected events
        if len(typesI) > 0 and len(typesC) == 0: # there is only instance events
            folium.Marker(
                location=[ea.getLatitude(),ea.getLongitude()],
                popup= "SL: " + str(ea.getSeverityLevel()) + "\n" + descriptions,
                icon=folium.Icon(color='orange', icon="info", prefix='fa'),
            ).add_to(map)
        elif len(typesI) == 0 and len(typesC) > 0: # only complex events
            folium.Marker(
                location=[ea.getLatitude(),ea.getLongitude()],
                popup= "SL: " + str(ea.getSeverityLevel())  + "\n" +  descriptions,
                icon=folium.Icon(color='darkpurple', icon='info', prefix='fa'),
            ).add_to(map)
        else : #both instance and complex events
            folium.Marker(
                location=[ea.getLatitude(),ea.getLongitude()],
                popup= "SL: " + str(ea.getSeverityLevel())  + "\n" + descriptions,
                icon=folium.Icon(color='red', icon='info', prefix='fa'),
            ).add_to(map)
            
    ## Creating the html file
    map.save(requestEA + ".html")

    if debug:
        print ("Creating new MAP with all received emergency alarms")

    ## Releasing this method to be used by other thread
    lock.release()

##############################################################################

def on_connect(client, userdata, flags, rc):
    global debug, ipBroker

    if debug:
        print("Connected to the MQTT Broker:", ipBroker)

##############################################################################

def on_disconnect(client, userdata, rc):
    global debug

    if debug:
        print("Disconnected from the MQTT Broker")

##############################################################################

def on_message(client, userdata, message):
    global debug, alarms

    ## Received message (alarm) from the MQTT broker
    received = message.payload.decode()

    if debug:
        print("Received Emergency Alarm:")
        print(received) # it is in the JSON format

    try:
        ## Reconstructing the EA
        parsed_data = json.loads(received)
        ea = EA(parsed_data["id"], parsed_data["timestamp"], parsed_data["gps"]["la"],parsed_data["gps"]["lo"])
        ea.setSeverityLevel(parsed_data["sl"])
        typesI = parsed_data["typesInstance"]
        typesC = parsed_data["typesComplex"]

        # insert the detected events in the EA 
        for y in typesI:
            ea.putEventInstance(y)
        for w in typesC:
            ea.putEventComplex(w)

        ## Inserting (updating) alarm
        alarms.putAlarm(ea, debug)

        plotMap()

    except Exception as e:
        print ("Error when processing EA...")
        print (e)

##############################################################################

# Called when program exits
def exit_handler():
    global debug

    if debug:
        print("Emergency Alarm Client is exiting...")

##############################################################################

## Main code of the EAC_Map
def main(argv):
    global requestEA, ipBroker, debug

    ## Parse arguments from the command-line
    ## Options: debug idU ipEPU portEPU
    opts, ars = getopt.getopt(argv, "hd:i:m:", ["debug=", "ipBroker=", "requestEA="])
    for opt, arg in opts:
        if opt == "-h":
            print("edu.py -d <debug> -i <ipBroker> -m <requestEA>")
            sys.exit(1)
        elif opt in ("-d", "--debug"):
            if arg == "True":
                debug = True
            else:
                debug = False
        elif opt in ("-i", "--ipBroker"):
            ipBroker = arg
        elif opt in ("-m", "--requestEA"):
            requestEA = arg
    ########

    if debug:
        print("Initializing the EAC for emergencies visualization...")

    ## MQTT subscriptions and initial configuration
    clientmqtt = mqtt.Client("")
    clientmqtt.on_connect = on_connect
    clientmqtt.on_disconnect = on_disconnect
    clientmqtt.on_message = on_message

    clientmqtt.connect(ipBroker)
    clientmqtt.subscribe(requestEA)

    if debug:
        print("Subscribing to the MQTT Broker with topic:", requestEA)

    ## It is used to update the current detected EA in the map
    mapRefresher().start()

    atexit.register(exit_handler)

    ## Keep receiving MQTT messages indefinitely
    clientmqtt.loop_forever()

##############################################################################

if __name__ == '__main__':
    main(sys.argv[1:])
