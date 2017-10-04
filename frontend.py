import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop
import Adafruit_DHT  # DHT
import Adafruit_BMP.BMP085 as BMP085 # BMP
import threading # DS

DHT_PIN = 17

SECURE = 0
PASS =
PASS_COUNT = 0

SET_AIR_TEMP = 0
SET_FLOOR_DELTA = 0
AIR_TEMP_STOCK = 23
FLOOR_DELTA_STOCK = 1.5

HOURS_STOCK = '5 7 13 16 17 19 22'
SET_HOURS = 0

BMP_T = 0
BMP_P = 0
DS_1 = 0
DS_2 = 0
DHT_H = 0
DHT_T = 0

air_temp_path = 'air_temp'
floor_delta_path = 'floor_delta'
relay_switch_path = 'relay_switch'
hours_path = 'hours'

ds_1_path = '/sys/bus/w1/devices/28-0516814060ff/w1_slave'
ds_2_path = '/sys/bus/w1/devices/28-05169410e9ff/w1_slave'

try:
    air = open(air_temp_path)
except:
    air = open (air_temp_path, 'w')
    air.write(str(AIR_TEMP_STOCK))

try:
    floor = open(floor_delta_path)
except:
    floor = open(floor_delta_path, 'w')
    floor.write(str(FLOOR_DELTA_STOCK))
try:
    hours = open(hours_path)
except:
    hours = open(hours_path, 'w')
    hours.write(str(HOURS_STOCK))

AIR_TEMP=air.read()
FLOOR_DELTA = floor.read()
HOURS = hours.read()
hours.close()
floor.close()
air.close()

if str(AIR_TEMP) == "":
    AIR_TEMP = AIR_TEMP_STOCK

if str(FLOOR_DELTA) == '':
    FLOOR_DELTA = FLOOR_DELTA_STOCK

if str(HOURS) == '':
    HOURS = HOURS_STOCK

# define sensors for DHT and BMP
sensor_dht = Adafruit_DHT.DHT22
sensor_bmp = BMP085.BMP085()

def get_values():
        global BMP_T
        global BMP_P
        global DS_1
        global DS_2
        global DHT_H
        global DHT_T

        DHT_H, DHT_T = Adafruit_DHT.read_retry(sensor_dht, DHT_PIN)
        BMP_T = sensor_bmp.read_temperature()
        BMP_P = sensor_bmp.read_pressure()*0.0075006375541921

        def temp1():
            global DS_1
            tempfile1 = open(ds_1_path)
            thetext1 = tempfile1.read()
            tempfile1.close()
            tempdata1 = thetext1.split("\n")[1].split(" ")[9]
            DS_1 = float(tempdata1[2:])/1000

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

def enable_relay():
    f = open(relay_switch_path, 'w')
    f.write('on')
    f.close()

def disable_relay():
    f = open(relay_switch_path, 'w')
    f.write('off')
    f.close()

def auto_relay():
    f = open(relay_switch_path, 'w')
    f.write('auto')
    f.close()

def write_floor_delta():
    f = open(floor_delta_path, 'w')
    f.write(str(FLOOR_DELTA))
    f.close()

def write_air_temp():
    f = open(air_temp_path, 'w')
    f.write(str(AIR_TEMP))
    f.close()

def write_hours():
    f = open(hours_path, 'w')
    f.write(str(HOURS))
    f.close()

def handle(msg):
    global SECURE
    global PASS
    global PASS_COUNT

    global SET_AIR_TEMP
    global AIR_TEMP

    global SET_FLOOR_DELTA
    global FLOOR_DELTA

    global HOURS
    global SET_HOURS

    chat_id = msg['chat']['id']
    command = msg['text']

    print 'Got command: %s' % command

    if SECURE == 0 and command[0][0] == '/':
        if PASS_COUNT < 4:
            bot.sendMessage(chat_id, "Enter password")
        elif PASS_COUNT == 4:
            bot.sendMessage(chat_id, "See you later!")
    elif command == '/start':
            bot.sendMessage(chat_id,
        "  /get - get status and values from sensors"
        + "\n /relay_on - Enable relay"
        + "\n /relay_off - Disable relay"
        + "\n /relay_auto - AUTO MODE"
        + "\n /set_air_temp - Set up AIR_TEMP"
        + "\n /set_floor_delta - Set up delta between grebyonka"
        + "\n /set_hours - Se up hours when relay will be enable in AUTO mode"
        + "\n /set_default_hours - reset all to default"
        )
    elif command == '/set_air_temp':
        SET_AIR_TEMP = 1
        bot.sendMessage(chat_id, "Enter value")
    elif command == '/set_floor_delta':
        SET_FLOOR_DELTA = 1
        bot.sendMessage(chat_id, "Enter value")
    elif command == '/set_hours':
        SET_HOURS = 1
        bot.sendMessage(chat_id, "Enter values separated by space")
    elif command == '/set_default_hours':
        HOURS = HOURS_STOCK
        write_hours()
        bot.sendMessage(chat_id, "HOURS now is " + str(HOURS))
    elif command == '/relay_on':
        bot.sendMessage(chat_id, "Relay enabled")
        enable_relay()
    elif command == '/relay_off':
        bot.sendMessage(chat_id, "Relay disabled")
        disable_relay()
    elif command == '/relay_auto':
        bot.sendMessage(chat_id, "Relay in auto mode")
        auto_relay()
    elif command == '/get':
        get_values()
        file_relay = open (relay_switch_path, 'r')
        file_hours = open (hours_path, 'r')
        bot.sendMessage(chat_id,
        "RELAY MODE STATUS: " + file_relay.read()
        + "\nDS_1 = " + str(DS_1) + " C"
        + "\nDS_2 = " + str(DS_2) + " C"
        + "\nBMP_PRESS = " + str(BMP_P) + " hg mm"
        + "\nBMP_TEMP = " + str(BMP_T) + " C"
        + "\nDHT_H = " + str(DHT_H) + " %"
        + "\nDHT_T = " + str(DHT_T) + " C"
        + "\nFLOOR_DELTA = " + str(FLOOR_DELTA) + " C"
        + "\nAIR_TEMP = " + str(AIR_TEMP) + " C"
        + "\nHOURS = " + file_hours.read())
        file_relay.close()
        file_hours.close()
    else:
        if SET_AIR_TEMP == 1:
            SET_AIR_TEMP = 0
            AIR_TEMP = command
            write_air_temp()
            bot.sendMessage(chat_id, "AIR_TEMP now is " + str(AIR_TEMP))

        elif SET_FLOOR_DELTA == 1:
            SET_FLOOR_DELTA = 0
            FLOOR_DELTA = command
            write_floor_delta()
            bot.sendMessage(chat_id, "FLOOR_DELTA now is " + str(FLOOR_DELTA))

        elif SET_HOURS == 1:
            SET_HOURS = 0
            HOURS = command
            write_hours()
            bot.sendMessage(chat_id, "HOURS now is " + str(HOURS))

        elif SECURE == 0:
            if PASS_COUNT > 3:
                bot.sendMessage(chat_id, "Get the fuck out!")

            elif str(PASS)==command:
                bot.sendMessage(chat_id, "Nice, now You can use /start or etc")
                SECURE = 1
                PASS_COUNT = 0

            else:
                bot.sendMessage(chat_id, "Wrong pass, keep in ur mid that u have 4 attemtps")
                PASS_COUNT+=1

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)