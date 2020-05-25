Emergencies Processing Unit - Visual Sensing extension

Default TCP port to receive Events Reports: 55055

Dafault values of constants:
fe = 0.4
fr = 0.3
ft = 0.3
Medium in the Gaussian function = 12
Standard deviation in the Gaussian function = 6

Three Risk Zones as default values (la, lo, radius(km), rz)
definedRZ = [[41.179220,-8.597667,5,70], \
             [41.185324,-8.696129,5,50], \
             [41.129798,-8.607621,5,100]]

The EPU may receive three different parameters as command-line arguments:
-d debug (True or False)
-e idEPU (the numerical id of EPU)
-i ipBroker (the IP address of the MQTT Broker - default port is considered)
