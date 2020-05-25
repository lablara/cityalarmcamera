# **************************************************
# Accessory classes for the EDU for scalar and visual sensing
# They model the concepts of Event of Interest and Events Report
# The concepts of instance and complex events are modelled here
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 12/05/2020
#**************************************************

import json

###################################################
## Models a list of all EI
class ListEI:   
    
    def __init__(self):
        self.eventsInstance = []
    
    def putEvent(self, y, th, math, txt):
        ## math describes if the symbol is <= (0) or >= (1)
        event = EI(y, th, math, txt)
        self.eventsInstance.append(event)        
    
    def removeEvent(self, event):
        self.eventsInstance.remove(event)
    
    def getEvents (self):
        return self.eventsInstance
    
    def getEventY (self, y):
        for event in self.eventsInstance:
            if event.getType() == y:  #As the values of y are unique, there is only one answer here
                return event
    
    def getNumberDetectedEvents(self):
        number = 0
        for event in self.eventsInstance:
            if event.isDetected():
                number = number + 1
        
        return number
        
    def printValues(self):
        for event in self.eventsInstance:
            if event.getMath() == 0:
                print ("Type:",  event.getType(),  ": Threshold =", event.getThreshold(), ": Symbol is <=. Description:", event.getDescription())
            else:
                print ("Type:",  event.getType(),  ": Threshold =", event.getThreshold(), ": Symbol is >=. Description:", event.getDescription())

## Models an Event of Interest - INSTANCE
class EI:
    
    def __init__(self, idy, th, m, text):
        self.y = idy
        self.detected = False
        self.threshold = th
        self.math = m
        
        #this is not in CityAlarm paper, but it may help to "track" events
        self.description = text 

    def getType (self):
        return self.y
    
    def getThreshold (self):
        return self.threshold

    def getDescription (self):
        return self.description

    def getMath (self):
        return self.math

    def setDetected (self):
        self.detected = True
    
    def setUndetected (self):
        self.detected = False
    
    def isDetected (self):
        return self.detected
    
    
#############################################

## Models a list of all Events
class ListEC:
    
    def __init__(self):
        self.eventsComplex = []
    
    def putEvent(self, w, txt):
        ## math describes if the symbol is <= (0) or >= (1)
        event = EC(w, txt)
        self.eventsComplex.append(event)        
    
    def removeEvent(self, event):
        self.eventsComplex.remove(event)
    
    def getEvents (self):
        return self.eventsComplex
    
    def getEventW (self, w):
        for event in self.eventsComplex:
            if event.getType() == w:  #As the values of y are unique, there is only one answer here
                return event
    
    def getNumberDetectedEvents(self):
        number = 0
        for event in self.eventsComplex:
            if event.isDetected():
                number = number + 1
        
        return number
        
    def printValues(self):
        for event in self.eventsComplex:
            print ("Type:",  event.getType(),  ", Description:", event.getDescription())

## Models an Event of Interest - COMPLEX
class EC:
    
    def __init__(self, idw, text):
        self.w = idw
        self.detected = False
        
        self.description = text 

    def getType (self):
        return self.w
 
    def getDescription (self):
        return self.description

    def setDetected (self):
        self.detected = True
    
    def setUndetected (self):
        self.detected = False
    
    def isDetected (self):
        return self.detected
    
## Models an Events Report    
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
        return self.la

    def getLongitude (self):
        return self.lo
    
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
   
#####################################################
## Supportive class for the JSON convertion
class GPS():
    def __init__(self, latitude, longitude):
        self.la = latitude
        self.lo = longitude
