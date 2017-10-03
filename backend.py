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

air_temp_path = 'air_temp'
floor_delta_path = 'floor_delta'

try:
    air = open(air_temp_path, 'r')
except:
    print 'air file doesnt exist'

AIR_TEMP=air.read()

if str(AIR_TEMP) == "":
    AIR_TEMP = 22

try:
    floor = open(floor_delta_path, 'r')
except:
    print 'floor file doesnt exist'

FLOOR_DELTA = floor.read()

if str(FLOOR_DELTA) == '':
    FLOOR_DELTA = 1.5

# define sensors for DHT and BMP
sensor_dht = Adafruit_DHT.DHT22
sensor_bmp = BMP085.BMP085()
temp_bmp = 0
press_bmp = 0
DS_1 = 0
DS_2 = 0
humid_dht = 0
temp_dht = 0

def get_values():
        global temp_bmp
        global press_bmp
        global DS_1
        global DS_2
        global humid_dht
        global temp_dht

        humid_dht, temp_dht = Adafruit_DHT.read_retry(sensor_dht, DHT_PIN)
        temp_bmp=sensor_bmp.read_temperature()
        press_bmp=sensor_bmp.read_pressure()*0.0075006375541921
        DS_1 = 0
        DS_2 = 0

        def temp1():
            global DS_1
            tempfile1 = open("/sys/bus/w1/devices/28-0516814060ff/w1_slave")
            thetext1 = tempfile1.read()
            tempfile1.close()
            tempdata1 = thetext1.split("\n")[1].split(" ")[9]
            DS_1 = float(tempdata1[2:])/1000

        def temp2():
            global DS_2
            tempfile2 = open("/sys/bus/w1/devices/28-05169410e9ff/w1_slave")
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
    f = open('relay_switch', 'r')
    RELAY_STATUS = f.read()
def get_floor_delta():
    global FLOOR_DELTA
    f = open(floor_delta_path, 'r')
    FLOOR_DELTA = f.read()
def get_air_temp():
    global AIR_TEMP
    f = open(air_temp_path, 'r')
    AIR_TEMP = f.read()
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

    DS_DELTA = DS_2 - DS_1
    TEMP_AVR = (temp_bmp + temp_dht) / 2
    if str(RELAY_STATUS) == "":
        print "\n RELAY MODE STATUS is empty, using AUTO"
        RELAY_STATUS = 'auto'

    if str(AIR_TEMP) == '':
        print '\n AIR_TEMP is empty, using stock'
        AIR_TEMP = 23

    if str(FLOOR_DELTA) == '':
        print '\n FLOOR_DELTA is empty, using stock'
        FLOOR_DELTA = 1.5

    print ("\n DS DELTA " + str(DS_DELTA) + " vs FLOOR DELTA " + str(FLOOR_DELTA)
            + "\n TEMP AVR " + str(TEMP_AVR) + " vs AIR TEMP " + str(AIR_TEMP)
            + "\n RELAY MODE STATUS " + str(RELAY_STATUS)
            + " \n RELAY " + str(GPIO_STAT))


    if str(RELAY_STATUS) == 'on':
        enable_relay()
    elif str(RELAY_STATUS) == 'off':
        disable_relay()
    elif str(RELAY_STATUS) == 'auto':
        if TEMP_AVR < AIR_TEMP and DS_DELTA > FLOOR_DELTA:
            enable_relay()
        else:
            disable_relay()

    time.sleep(2)
