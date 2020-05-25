# *********************************************************************
# Accessory classes for the EPU with the extension for Visual Sensing
# They model the concepts of Events Report and Emergency Alarm
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 2020/05/12
# *********************************************************************

import json

########################################################

## Just like in the EDU
class ER:

    def __init__(self, u, i, ts, latitude, longitude):
        self.edu = u
        self.id = i
        self.timestamp = ts
        self.gps = GPS(latitude,longitude)
        self.eventsInstance = []  # array of integers (types of detected events - instance)
        self.eventsComplex = []  # array of integers (types of detected events - complex)

    def putEventTypeInstance(self, y):
        self.eventsInstance.append(y)

    def putEventTypeComplex(self, w):
        self.eventsComplex.append(w)

    def getTimestamp (self):
        return self.timestamp

    def getLatitude (self):
        return self.gps.getLatitude()

    def getLongitude (self):
        return self.gps.getLongitude()

    def getEventsTypesInstance (self):
        return self.eventsInstance

    def getEventsTypesComplex (self):
        return self.eventsComplex

    def getNumberEI(self):
        return len(self.eventsInstance)  # Number of EI (Instance) in the ER

    def getNumberEC(self):
        return len(self.eventsComplex)  # Number of EC (Complex) in the ER

    def printValues(self):
        for y in self.eventsInstance:
            print ("Type instance =",  y)
        for w in self.eventsComplex:
            print ("Type complex =",  w)

    ## This is required to convert the ER to JSON
    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True, indent=4)

########################################################

## Supportive class for the JSON conversion
class GPS():
    def __init__(self, latitude, longitude):
        self.la = latitude
        self.lo = longitude
    
    def getLatitude(self):
        return self.la

    def getLongitude(self):
        return self.lo

########################################################

class RiskZone():
    ## Basic definitions of the risk zones
    def __init__(self, i, latitude, longitude, radius, risk):
        self.id = i
        self.gps = GPS(latitude,longitude)
        self.dz = radius
        self.rz = risk

    def getId(self):
        return self.id

    def getRZ(self):
        return self.rz

    def getLatitude (self):
        return self.gps.la

    def getLongitude (self):
        return self.gps.lo

    def getRadius(self):
        return self.dz

    def printValues(self):
        print ("Latitude:",self.gps.la,", Longitude:",self.gps.lo,", Radius",self.dz,", Risk level:",self.rz)

########################################################

# Definition of an Emergency Alarm
class EA():
    def __init__(self, i, ts, latitude, longitude):
        self.id = i
        self.gps = GPS(latitude,longitude)
        self.timestamp = ts
        
        ## Only the types of the detected events - It makes easier to handle them in the EPU and the clients
        self.typesInstance = []
        self.typesComplex = []
        
        ## Severity level
        self.sl = 0

    def getLatitude (self):
        return self.gps.getLatitude()

    def getLongitude (self):
        return self.gps.getLongitude()

    def putEventInstance(self, y):
        self.typesInstance.append(y)

    def putEventComplex(self, w):
        self.typesComplex.append(w)

    def getEventsTypesInstance (self):
        return self.typesInstance

    def getEventsTypesComplex (self):
        return self.typesComplex

    def setSeverityLevel(self, sev):
        self.sl = sev

    def getSeverityLevel (self):
        return self.sl

    def getId(self):
        return self.id

    def printValues(self):
        print ("EA id:",self.id,", Timestamp:",self.timestamp,", Latitude:",self.gps.la,", Longitude:",self.gps.lo, " SL:", self.sl)
        if len(self.typesInstance) > 0:
            print ("This EA has the following EI types:")
            for e in self.typesInstance:
                print ("Type:", e)
        else:
            print ("This EA has no instance event")
        
        if len(self.typesComplex) > 0:
            print ("This EA has the following EC types:")
            for e in self.typesComplex:
                print ("Type:", e)
        else:
            print ("This EA has no complex event")

    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True, indent=4)
