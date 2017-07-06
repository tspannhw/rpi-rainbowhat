#!/usr/bin/env python
import time
import colorsys
import os
import json
import sys, socket
import subprocess
import time
import datetime
from time import sleep
from time import gmtime, strftime

import rainbowhat

#### Constants

QNH=1020

RAINBOW_BRIGHTNESS = 255

HUE_COLD = 225
HUE_WARM = 0

T_COLD = 15
T_WARM = 30

running = 1

#### Initialization
# yyyy-mm-dd hh:mm:ss
currenttime= strftime("%Y-%m-%d %H:%M:%S",gmtime())

external_IP_and_port = ('198.41.0.4', 53)  # a.root-servers.net
socket_family = socket.AF_INET

host = os.uname()[1]

#### Methods

def getAltitude(qnh, pressure):
    """Return the current approximate altitude.
    :param qnh: Your local value for atmospheric pressure adjusted to sea level.
    """
    return 44330.0 * (1.0 - pow(pressure / (qnh*100), (1.0/5.255))) # Calculate altitute from pressure & qnh

def display_message(message):
    rainbowhat.display.print_str(message)
    rainbowhat.display.show()

def display_float(fval):
    rainbowhat.display.print_float(fval)
    rainbowhat.display.show()

@rainbowhat.touch.A.press()
def touch_a(channel):
    global ftemp
    display_float(ftemp)

@rainbowhat.touch.B.press()
def touch_b(channel):
    global temperature
    display_float(temperature)

@rainbowhat.touch.C.press()
def touch_c(channel):
    global altitude
    display_float(altitude)

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

def set_rainbow(temp):
    temp = max(temp,T_COLD)
    temp = min(temp,T_WARM)

    temp -= T_COLD
    temp /= float(T_WARM - T_COLD)

    hue = (1.0-temp) * abs(HUE_WARM - HUE_COLD) / 360.0

    r, g, b = [int(c * 255) for c in  colorsys.hsv_to_rgb(hue, 1.0, 1.0)]

    rainbowhat.rainbow.set_all(r, g, b, brightness=0.1)
    rainbowhat.rainbow.show()

def IP_address():
        try:
            s = socket.socket(socket_family, socket.SOCK_DGRAM)
            s.connect(external_IP_and_port)
            answer = s.getsockname()
            s.close()
            return answer[0] if answer else None
        except socket.error:
            return None

def output_row():
    global temperature
    global pressure
    global altitude
    global cpuTemp
    global calctemp
    global ftemp

    temperature = rainbowhat.weather.temperature()
    pressure = rainbowhat.weather.pressure()
    altitude = getAltitude(QNH, pressure)
    cpuTemp=int(float(getCPUtemperature()))
    calctemp = temperature - ((cpuTemp - temperature)/ 1.5)
    ftemp = 9.0/5.0 * calctemp + 32
    ipaddress = IP_address()

    row =  { 'ts': currenttime, 'host': host, 'cputemp': round(cpuTemp,2), 'ipaddress': ipaddress, 'temp': round(temperature,2), 'tempf': round(ftemp,2), 'pressure': round(pressure,2), 'altitude': round(altitude,2), 'tempf2': round(calctemp,2) }
    json_string = json.dumps(row)
    print(json_string)

#    print 'Temperature: {0:0.1f} C'.format(temperature)
#    print 'CPU: {0:0.1f} C'.format(cpuTemp)
#    print 'Corrected Temp: {0:0.1f} C'.format(calctemp)
#    print 'Room Temp: {0:0.1f} F'.format(ftemp)
#    print 'Pressure:    {0:0.1f} Pa'.format(pressure)
#    print 'Altitude:  {0:0.1f}'.format(altitude)

output_row()
sleep(5)
rainbowhat.display.clear()
rainbowhat.display.show()
