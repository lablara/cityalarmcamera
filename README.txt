# cityalarmcamera
Implementation of the CityAlarm Emergency Alerting system with an extension for visual sensing
This implementation allows the processing of both Instance and Complex events

This project is divided in three elements:

Events Dectection Unit (EDU), Emergencies Processing Unit (EPU) and Emergency Alarms Client (EAC)

All codes are written in Python3, using some additional libraries

*******************************************************************

The EDU is implemented around the GrovePi+ hardware framework

The GrovePi+ has to be installed and enabled, as specified by the manufacturer. The following link describes all the required steps to allow the use of GrovePi+ in the Raspberry Pi: https://www.dexterindustries.com/GrovePi/get-started-with-the-grovepi/

Before using the EDU, one additional library has also to be installed through the following command:

pip3 install numpy

As a second remark about the EDU and the GrovePi+, the GPS module operates through the serial port of Raspberry and thus the Bluetooth module needs to be deactivated in some versions, as well as some configurations for the system kernel may be required. For the Raspberry Pi 3:

Step 1:
in /boot/config.txt, add at the end of the file:
dtoverlay=pi3-miniuart-bt
dtoverlay=pi3-disable-bt
enable_uart=1

Step 2:
in /boot/cmdline.txt remove:
console=ttyAMA0,115200 console=tty1
and add:
plymouth.ignore-serial-consoles

The EDU also requires the OpenCV lib, which have to be installed. The following link describes all the required steps to install OpenCV (versions 4.x) and additional libraries: https://blog.piwheels.org/new-opencv-builds-including-opencv-4-x/

Additionally, the following installation command is required:

pip3 install matplotlib

*******************************************************************

For the EPU, the haversine lib has to be installed:

pip3 install haversine

For the EPU and the EAC, the paho-mqtt library has also to be installed, using the following command:

pip3 install paho-mqtt

*******************************************************************

For the EAC app, the folium library has to be installed through the following command:

pip3 install folium
