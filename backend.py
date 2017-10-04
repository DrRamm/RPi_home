import time
import random
import datetime
import RPi.GPIO as GPIO   # GPIO
import Adafruit_DHT  # DHT
import Adafruit_BMP.BMP085 as BMP085 # BMP
import threading # DS

DHT_PIN = 17

RELAY_PIN = 24
RELAY_STATUS = 0
GPIO_STAT = 0

AIR_TEMP_STOCK = 23
FLOOR_DELTA_STOCK = 1.5
HOURS_STOCK = '5 7 13 16 17 19 22'

air_temp_path = 'air_temp'
floor_delta_path = 'floor_delta'
relay_switch_path = 'relay_switch'
hours_path = 'hours'

ds_1_path = '/sys/bus/w1/devices/28-0516814060ff/w1_slave'
ds_2_path = '/sys/bus/w1/devices/28-05169410e9ff/w1_slave'

try:
    air = open(air_temp_path, 'r')
except:
    print '\n air file doesnt exist'

try:
    floor = open(floor_delta_path, 'r')
except:
    print '\n floor file doesnt exist'

try:
    hours = open(hours_path, 'r')
except:
    print '\n hours file doesnt exist'

# get temp from last tg command
AIR_TEMP=air.read()
FLOOR_DELTA = floor.read()
HOURS = hours.read()

if str(AIR_TEMP) == '':
    AIR_TEMP = AIR_TEMP_STOCK
if str(FLOOR_DELTA) == '':
    FLOOR_DELTA = FLOOR_DELTA_STOCK
if str(HOURS) == '':
    HOURS = HOURS_STOCK

# define sensors for DHT and BMP
sensor_dht = Adafruit_DHT.DHT22
sensor_bmp = BMP085.BMP085()

#initial stuff
BMP_T = 0
BMP_P = 0
DS_1 = 0
DS_2 = 0
DHT_H = 0
DHT_T = 0

def get_values():
        global BMP_T
        global BMP_P
        global DS_1
        global DS_2
        global DHT_H
        global DHT_T

        DHT_H, DHT_T = Adafruit_DHT.read_retry(sensor_dht, DHT_PIN)
        BMP_T=sensor_bmp.read_temperature()
        BMP_P=sensor_bmp.read_pressure() * 0.0075006375541921

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

        t1 = threading.Thread(target=temp1)
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target=temp2)
        t2.daemon = True
        t2.start()

        while DS_1 == 0 or DS_2 == 0:
            time.sleep(0.1)

def get_relay_status():
    global RELAY_STATUS
    f = open(relay_switch_path, 'r')
    RELAY_STATUS = f.read()
    if str(RELAY_STATUS) == "":
        print "\n RELAY MODE STATUS is empty, using AUTO"
        RELAY_STATUS = 'auto'

def get_floor_delta():
    global FLOOR_DELTA
    f = open(floor_delta_path, 'r')
    FLOOR_DELTA = f.read()
    if str(FLOOR_DELTA) == '':
        print '\n FLOOR_DELTA is empty, using stock'
        FLOOR_DELTA = FLOOR_DELTA_STOCK

def get_air_temp():
    global AIR_TEMP
    f = open(air_temp_path, 'r')
    AIR_TEMP = f.read()
    if str(AIR_TEMP) == '':
        print '\n AIR_TEMP is empty, using stock'
        AIR_TEMP = AIR_TEMP_STOCK

def get_hours():
    global HOURS
    f = open(hours_path, 'r')
    HOURS = f.read()
    if str(HOURS) == '':
        print '\n HOURS is empty, using stock'
        HOURS = HOURS_STOCK

def enable_relay():
    global GPIO_STAT
    if GPIO_STAT == 0:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO_STAT = 1
        time.sleep(0.3)
        print '\n Relay enabled'

def disable_relay():
    global GPIO_STAT
    if GPIO_STAT == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        GPIO_STAT = 0
        time.sleep(0.3)
        print '\n Relay disabled'

while True:
    get_values()
    get_relay_status()
    get_air_temp()
    get_floor_delta()
    get_hours()

    DS_DELTA = DS_2 - DS_1
    TEMP_AVR = (BMP_T + DHT_T) / 2
    CURR_HOUR = str(int(time.strftime("%-H")) + 3)

    # Parsing hours
    HOURS_RELAY_ENABLE = 0
    HOURS_LIST = HOURS.split(" ")
    for temp in HOURS_LIST:
        if str(temp) == str(CURR_HOUR):
            HOURS_RELAY_ENABLE = 1

    print ("\n DS DELTA " + str(DS_DELTA) + " vs FLOOR DELTA " + str(FLOOR_DELTA)
            + "\n TEMP AVR " + str(TEMP_AVR) + " vs AIR TEMP " + str(AIR_TEMP)
            + "\n RELAY MODE STATUS " + str(RELAY_STATUS)
            + " \n RELAY " + str(GPIO_STAT)
            + "\n HOURS " + str(HOURS) + " vs CURR HOUR " + str(CURR_HOUR)
            + "\n HOURS RELAY STATUS " + str(HOURS_RELAY_ENABLE))

    if str(RELAY_STATUS) == 'on':
        enable_relay()
    elif str(RELAY_STATUS) == 'off':
        disable_relay()
    elif str(RELAY_STATUS) == 'auto':
        if TEMP_AVR < AIR_TEMP and DS_DELTA > FLOOR_DELTA and HOURS_RELAY_ENABLE == 1:
            enable_relay()
        else:
            disable_relay()
    time.sleep(2)
