# -*- coding: utf-8 -*-
import time
import random
import datetime
import threading # DS
import Adafruit_DHT  # DHT
import RPi.GPIO as GPIO   # GPIO
import Adafruit_BMP.BMP085 as BMP085 # BMP
from datetime import  date

DHT_PIN = 17

RELAY_PIN = 24
RELAY_STATUS = 0

GPIO.setmode(GPIO.BCM)

HOURS_STOCK = '1 3 5 6 7 13 16 18 19 20 22'
HOURS_STOCK_WEND = '1 3 5 6 7 9 14 15 16 17 18 19 20 22'

HOME_PATH = "/home/pi/"
air_and_floor_path = HOME_PATH + 'deltas'
relay_mode_path = HOME_PATH + 'relay_mode'
hours_path = HOME_PATH + 'hours'
hours_wend_path = HOME_PATH + 'hours_wend'
hours_mode_path = HOME_PATH + 'hours_mode'
all_values_path = HOME_PATH + 'all_values'

ds_1_path = '/sys/bus/w1/devices/28-0516814060ff/w1_slave'
ds_2_path = '/sys/bus/w1/devices/28-05169410e9ff/w1_slave'

# define sensors for DHT and BMP
sensor_dht = Adafruit_DHT.DHT22
try:
    sensor_bmp = BMP085.BMP085()
except:
    print "bmp is shit"

#initial stuff
BMP_T = 0
BMP_P = 0
DS_1 = 0
DS_2 = 0
DHT_H = 0
DHT_T = 0

def write_all():
    f = open(all_values_path, 'w')
    f.write(
        str(DS_1) + " " +
        str(DS_2) + " " +
        str(BMP_T) + " " +
        str(BMP_P) + " " +
        str(DHT_H) + " " +
        str(DHT_T) + " " +
        str(RELAY_STATUS)
        )
    f.close()

def read_file(file_name):
    f = open(file_name, 'r')
    temp = f.read()
    f.close()
    return temp

def get_relay_mode():
    temp = ""
    temp = read_file(relay_mode_path)

    if str(temp) == "":
        print "\n RELAY MODE is empty, using AUTO"
        temp = 'auto'
    return temp

def get_air_and_floor():
    global FLOOR_DELTA_MIN
    global AIR_TEMP
    global FLOOR_DELTA_MAX

    FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX = read_file(air_and_floor_path).split(" ")

    if str(AIR_TEMP) == '':
        print '\n AIR_TEMP is empty, using stock'
        AIR_TEMP = 26.5

    if str(FLOOR_DELTA_MIN) == '':
        print '\n FLOOR_DELTA_MIN is empty, using stock'
        FLOOR_DELTA_MIN = 3

    if str(FLOOR_DELTA_MAX) == '':
        print '\n FLOOR_DELTA_MIN MAX is empty, using stock'
        FLOOR_DELTA_MAX = 13

def get_hours():
    global HOURS
    global HOURS_WEND

    HOURS = read_file(hours_path)
    HOURS_WEND = read_file(hours_wend_path)

    if str(HOURS) == '':
        print '\n HOURS is empty, using stock'
        HOURS = HOURS_STOCK

    if str(HOURS_WEND) == '':
        print '\n HOURS WEND is empty, using stock'
        HOURS_WEND = HOURS_WEND_STOCK

def get_hours_mode():
    temp = ""
    temp = read_file(hours_mode_path)

    if str(temp) == '':
        print '\n HOURS_MODE is empty,  enabled by default'
        temp = 'on'
    return temp

def enable_relay():
    global RELAY_STATUS
    if RELAY_STATUS == 0:
        GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)
        RELAY_STATUS = 1
        time.sleep(0.3)
        print '\n Relay enabled'

    write_all()

def disable_relay():
    global RELAY_STATUS

    if RELAY_STATUS == 1:
        GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
        RELAY_STATUS = 0
        time.sleep(0.3)
        print '\n Relay disabled'

    write_all()

def get_values():
        global BMP_T
        global BMP_P
        global DS_1
        global DS_2
        global DHT_H
        global DHT_T

        get_relay_mode()
        get_air_and_floor()
        get_hours()
        get_hours_mode()

        DHT_H, DHT_T = Adafruit_DHT.read_retry(sensor_dht, DHT_PIN)
        try:
            BMP_T = sensor_bmp.read_temperature()
            BMP_P = sensor_bmp.read_pressure() * 0.0075006375541921

        except:
            BMP_T=0
            BMP_P=0
        def temp1():
            global DS_1
            tempfile1 = open(ds_1_path)
            thetext1 = tempfile1.read()
            tempfile1.close()
            tempdata1 = thetext1.split("\n")[1].split(" ")[9]
            DS_1 = float(tempdata1[2:]) / 1000

        def temp2():
            global DS_2
            tempfile2 = open(ds_2_path)
            thetext2 = tempfile2.read()
            tempfile2.close()
            tempdata2 = thetext2.split("\n")[1].split(" ")[9]
            DS_2 = float(tempdata2[2:])/1000

        t1 = threading.Thread(target = temp1)
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target = temp2)
        t2.daemon = True
        t2.start()

        while DS_1 == 0 or DS_2 == 0:
            time.sleep(0.1)

while True:
    get_values()

    DS_DELTA = DS_2 - DS_1
    TEMP_AVR =  (BMP_T + DHT_T) / 2 if int(BMP_T) > 1 else DHT_T

    CURR_HOUR = int(time.strftime("%-H")) + 3
    NOW_DATE = datetime.date.today()

    # Parsing hours
    HOURS_RELAY_ENABLE = 0

    if NOW_DATE.isoweekday() == 6 or NOW_DATE.isoweekday() == 7:
        HOURS_LIST = HOURS_WEND.split(" ")
    else:
        HOURS_LIST = HOURS.split(" ")

    for temp in HOURS_LIST:
        if int(temp) == int(CURR_HOUR):
            HOURS_RELAY_ENABLE = 1
            break

    print ("\n FLOOR DELTA MIN " + str(FLOOR_DELTA_MIN) + " vs DS DELTA " + str(DS_DELTA) + " vs FLOOR DELTA MAX " + str(FLOOR_DELTA_MAX)
            + "\n TEMP AVR " + str(TEMP_AVR) + " vs AIR TEMP " + str(AIR_TEMP)
            + "\n RELAY MODE STATUS " + get_relay_mode()
            + "\n RELAY " + str(RELAY_STATUS)
            + "\n HOURS " + str(HOURS) + " vs CURR HOUR " + str(CURR_HOUR)
            + "\n HOURS RELAY STATUS " + str(HOURS_RELAY_ENABLE)
            + "\n NOW DATE " + str(NOW_DATE.isoweekday())
            + "\n NOW HOUR " + str(CURR_HOUR))

    if get_relay_mode() == 'on':
        enable_relay()
    elif get_relay_mode() == 'off':
        disable_relay()
    elif get_relay_mode() == 'auto':
        if float(TEMP_AVR) < float(AIR_TEMP) and float(DS_DELTA) > float(FLOOR_DELTA_MIN):
            if (get_hours_mode() == 'on' and int(HOURS_RELAY_ENABLE) == 1) or get_hours_mode() == 'off':
                enable_relay()
            else:
                disable_relay()
        elif float(DS_DELTA) > float(FLOOR_DELTA_MAX) and int(HOURS_RELAY_ENABLE) == 1:
            enable_relay()
        else:
            disable_relay()

time.sleep(10)