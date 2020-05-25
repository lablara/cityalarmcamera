#!/usr/bin/env python3

# *********************************************************************
# City Alarm with extension for Visual Sensing
# This is the Emergency Processor Unit (EPU) - It process both Instance and Complex events
# It receives Events Reports (ER) from the EDUs and generate Emergency Alarms (EA)
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 2020/05/12
# *********************************************************************

# Basic modules
import atexit
import socket
import threading
import json
import datetime
import haversine
import numpy as np
import sys, getopt

## Elements to support the operation of the EDU
from elementsEPU import ER, RiskZone, EA

## Supportive module to communicate through MQTT
from eaTransmitter import epuMQTT

########################################################
debug = True #Used to present trace messages on the screen

## There may be more than 1 EPU in operation. This parameter can be provided during initialization (command line)
idEPU = 1

## Required when computing the sl of the EA
fe = 0.4  #factor of events
fr = 0.3  #factor of Risk Zone
ft = 0.3  #factor of the time function
rmax = 100  #maximum impact of Risk Zone
tmax = 100  #maximum impact of the time function

## Keep track of generated Emergency Alarms
idEA = 1

## All defined Risk Zones
listRZ = []

## For temporal variable ct (gaussian)
## Check definitions in https://doi.org/10.3390/s20010170
mu = 12  #average
sigma = 6 #standard deviation

## To receive ER from the EDUs
localPort = 55055

## IP address of the MQTT Broker
## This parameter can be provided during initialization (command line)
ipBroker = "192.168.1.100"

## Definitions of the risk zones
## The format is [la,lo,radius,risk] - radius in km
## Defined locations are FEUP, Matosinhos and Gaia (Porto District, Portugal)
definedRZ = [[41.179220,-8.597667,50,70], \
                 [41.185324,-8.696129,20,50], \
                [41.129798,-8.607621,30,90]]


##############################################################################

## Receive ER from a EDU
class receiveERThread(threading.Thread):

    def __init__(self, c, a):
        self.connection = c
        self.address = a
        
        threading.Thread.__init__(self)

    def run(self):
        global idEA
        
        ## The ER that will be received
        er = None

        received = self.connection.recv(1024).decode('utf-8')

        # Reconstructing the ER from the JSON format to the object ER
        try:
            parsed_data = json.loads(received)
            er = ER(parsed_data["edu"], parsed_data["id"],parsed_data["timestamp"],parsed_data["gps"]["la"],parsed_data["gps"]["lo"])
            eventsInstance = parsed_data["eventsInstance"]
            eventsComplex = parsed_data["eventsComplex"]

            #Different types of events - Different procedures
            for y in eventsInstance:
                er.putEventTypeInstance (y)

            for w in eventsComplex:
                er.putEventTypeComplex(w)

            print ("Received ER from EDU n.", parsed_data["edu"])

        except:
            print ("Error when processing received ER..." + sys.exc_info()[0])

        ## Generating the EA
        numberEI = 0
        numberEC = 0
        if er is not None:
            ea = EA(idEA, er.getTimestamp(),er.getLatitude(),er.getLongitude())
            idEA = idEA + 1

            for y in er.getEventsTypesInstance():
                ea.putEventInstance(y)
                numberEI = numberEI + 1

            for w in er.getEventsTypesComplex():
                ea.putEventComplex(w)
                numberEC = numberEC + 1

            ## Compute the magnitude of the alarm
            computeSeveryLevel(ea, numberEI, numberEC)

            if debug:
                ea.printValues()

            ## Transmit the EA - MQQT Protocol
            transmitEA (ea)

        else:
            print ("Error processing ER when computing EA.")
			

##############################################################################

def initializeRiskZones():
    global listRZ

    idRZ = 1
    for rz in definedRZ:
        listRZ.append (RiskZone(idRZ,rz[0],rz[1],rz[2],rz[3]))
        idRZ = idRZ + 1

    if debug:
        print ("Defined Risk Zones:")
        for r in listRZ:
            r.printValues()

##############################################################################

def computeSeveryLevel(ea, ni, nc):
    global listRZ, fe, fr, ft, rmax, tmax

    if debug:
        print ("Computing the magnitude of the EA...")

    ## The impact of the Risk Zone on the emergency
    rz = computeAssociatedRZ(ea.getLatitude(),ea.getLongitude()) # Returns from 0 to rmax

    ## The impact of the temporal data on the emergency
    ta = computeTimeFunction() # Returns from 0 to tmax
    ct = computeGausseanFunction(datetime.datetime.today().hour) # Gaussian. Returns from 0.0 to 1.0

    nc = nc * 2 #complex events are twice as relevant as instance events
    nf = ni + nc #nf is a temporary variable to compute the sum of ni and nc, which must be lower than 5
    if nf > 5:
        nf = 5

    ## The magnitude of the EA is a function of nf + rz + ta
    sl = (nf * 20 * fe) + (((rz * 100) / rmax) * fr) + (((ta * 100) / tmax) * ft * ct)

    ## Truncate to avoid a too large float number
    sl =int(sl)

    if debug:
        print ("Sl of EA:", sl)

    ea.setSeverityLevel(sl)

##############################################################################

## This method verifies what is the current Risk Zone associated to the ER and returns the corresponding rz value
def computeAssociatedRZ(la,lo):
    global listRZ

    ## Given RZ center and the EDU position, is this distance minor than the defined radius of a RZ?
    edu = (la, lo)

    riskLevel = 0
    for rz in listRZ:
        zone = (rz.getLatitude(), rz.getLongitude())
        distance = haversine.haversine(edu,zone)

        if distance < rz.getRadius(): # The EDU is inside the Risk Zone
            if riskLevel < rz.getRZ(): # Update so the "best" RiskZone is chosen
                riskLevel = rz.getRZ()

    ## It will be 0 if the EDU is not in a Risk Zone
    return riskLevel

##############################################################################

def computeTimeFunction():
    ## There are different ways to implement this function
    ## We will consider a simple mapping between the day of the week
    global tmax

    ## Monday is 0 and Sunday is 6
    today = datetime.datetime.today().weekday()
    if 0 <= today <= 4: # from Monday to Friday
        return tmax
    elif today == 5:  # Saturday
        return tmax * 2 / 3
    else:   # Sunday
        return tmax / 3

##############################################################################

def computeGausseanFunction(x):
    ## Based on the Gaussian funciton described in CityAlarm paper
    ## x is the hour of the day
    global mu, sigma

    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))

##############################################################################

def transmitEA(ea):
    global idEPU, ipBroker

    ## Convert the Emergency Alarm to the JSON format
    jsonEA = ea.toJSON()

    if debug:
        print("\nTransmitting the Emergency Alarm", ea.getId())
        print("EA in the JSON format:")
        print (jsonEA)

    ## Connect to the MQTT Broker and publish the Emergency Alarm (JSON format)
    ## This class was created to support the communication to the MQTT
    epuMQTT(ipBroker,idEPU).publishEA (jsonEA) # This publishes the JSON-based EA to the MQTT Broker

##############################################################################

## Called when program exits
def exit_handler():
    if debug:
        print ("Emergency Processor Unit is exiting...")

##############################################################################

def main(argv):
    global idEPU, ipBroker, fe, fr, ft, localPort, debug

    ## Parse arguments from the command-line
    ## Options: debug idEPU ipMQTT
    opts, ars = getopt.getopt(argv, "hd:e:i:", ["debug=", "idEPU=", "ipBroker="])
    for opt, arg in opts:
        if opt == "-h":
            print("epu.py -d <debug> -e <idEPU> -i <ipBroker>")
            sys.exit(1)
        elif opt in ("-d", "--debug"):
            if arg == "True":
                debug = True
            else:
                debug = False
        elif opt in ("-e", "--idEPU"):   # Numerical id of the EDU
            idEPU = arg
        elif opt in ("-i", "--ipBroker"):   # IP address of the MQTT Broker
            ipBroker = arg
    ########

    if debug:
        print("Emergency Processor Unit is initializing...")

    ## Test if the constants fe, fr and ft are valuable (CityAlarm paper)
    if (fe + fr + ft) != 1.0:
        print("The sum of the calibration constants must be equal to 1.0. EPU exiting...")
        sys.exit(1)

    ## Create the Risk Zones according to the definitions
    initializeRiskZones()

    ## Receive ER from the EDU
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", localPort))

    print("EPU is ready and waiting connections at port", localPort, "...")
    ## Put the socket into listening mode
    s.listen()

    try:
        while True:
            ## Establish connection with EDU
            c, addr = s.accept()

            print('\nNew EDU connected:', addr[0], ':', addr[1])

            # Start a new thread to manage the communication and receive ER from the EDU
            receiveERThread(c, addr[0]).start ()

    except:
        print("EPU is closing due to some connection error...")
        s.shutdown(socket.SHUT_RDWR)

    atexit.register(exit_handler)

##############################################################################

if __name__ == '__main__':
    main(sys.argv[1:])
