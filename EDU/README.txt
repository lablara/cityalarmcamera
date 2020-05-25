Events Detection Unit

Default TCP port to send Events Reports: 55055

This implementation is a reference with the following sensors: temperature, humidity, noise, air quality and water. But any number of sensors can be easily inserted.

Default values of constants:
fs = 5
fx = 60

The EDU may receive four different parameters as command-line arguments:
-d debug (True or False)
-u idEDU (the numerical id of the EDU)
-i ipEPU (the IP address of the EPU)
-p portEPU (the TCP port of the EPU)
