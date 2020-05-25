# *********************************************************************
# These are supporting classes for the EAC, considering the extension for camera
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date         : 12/05/2020
# *********************************************************************

import time, datetime

##############################################################################

## Implements the idea of a list of Emergency Alarms
class ListEA:

    def __init__(self):
        self.alarms = []

    ## Insert a new EA into the list only if it comes from an unreported EDU
    def putAlarm(self, ea, debug):

        lat = ea.getLatitude()
        lon = ea.getLongitude()

        control = True
        ## Only insert new EA for new coordinates
        for alarm in self.alarms:
            if alarm.getLatitude() == lat and alarm.getLongitude() == lon:  ## Refresh alarm
                self.alarms.remove(alarm)
                self.alarms.append(ea)
                control = False
                if debug:
                    print("Removing old EA and inserting updated alarm...")

        if control:
            if debug:
                print ("Inserting new EA into the list...")
            self.alarms.append(ea)

    ## Remove old (not refreshed) EA
    def updateAlarms(self, maxTime, debug):

        t = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        now = t.timestamp()  # current absolute time (seconds)

        for alarm in self.alarms:
            alarmTime = datetime.datetime.strptime(alarm.getTimestamp(), "%a %b %d %H:%M:%S %Y").timestamp()

            if (now - alarmTime) > maxTime:  ## Old EA. Remove it
                self.alarms.remove(alarm)
                if debug:
                    print ("Removing old EA with id:", alarm.getId())

    def getAlarms(self):
        return self.alarms

    def printValues(self):
        for ea in self.alarms:
           print("Id:", ea.getId(), ": Latitude =", ea.getLatitude(), ": Longitude =", ea.getLongitude(), ": Severity =", ea.getSeverityLevel())

##############################################################################

## Definition of an Emergency Alarm
class EA():
    def __init__(self, i, ts, latitude, longitude):
        self.id = i
        self.gps = GPS(latitude,longitude)
        self.timestamp = ts
        self.typesInstance = []
        self.typesComplex = []
        self.sl = 0

    def getLatitude (self):
        return self.gps.la

    def getLongitude (self):
        return self.gps.lo

    def putEventInstance(self, y):
        self.typesInstance.append(y)
    
    def putEventComplex(self, y):
        self.typesComplex.append(y)

    def getEventsInstanceTypes (self):
        return self.typesInstance
    
    def getEventsComplexTypes (self):
        return self.typesComplex

    def setSeverityLevel(self, sev):
        self.sl = sev

    def getSeverityLevel (self):
        return self.sl

    def getId(self):
        return self.id

    def getTimestamp(self):
        return self.timestamp

    def printValues(self):
        print ("EA id:",self.id,", Timestamp:",self.timestamp,", Latitude:",self.gps.la,", Longitude:",self.gps.lo, " SL:", self.sl)
        print ("This EA has the following EI types:")
        for e in self.typesInstance:
            print ("Type:", e)
        print ("This EA has the following EC types:")
        for e in self.typesComplex:
            print ("Type:", e)

    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True, indent=4)

##############################################################################

class GPS():
    def __init__(self, latitude, longitude):
        self.la = latitude
        self.lo = longitude
