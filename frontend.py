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
AIR_TEMP_STOCK=22
FLOOR_DELTA_STOCK=1.5

temp_bmp=0
press_bmp=0
DS_1 = 0
DS_2 = 0
humid_dht = 0
temp_dht = 0

air_temp_path = 'air_temp'
floor_delta_path = 'floor_delta'

try:
    air = open(air_temp_path, )
except:
    air = open (air_temp_path, 'w')
    air.write(str(AIR_TEMP_STOCK))

AIR_TEMP=air.read()
air.close()

if str(AIR_TEMP) == "":
    AIR_TEMP = AIR_TEMP_STOCK

try:
    floor = open(floor_delta_path)
except:
    floor = open(floor_delta_path, 'w')
    floor.write(str(FLOOR_DELTA_STOCK))

FLOOR_DELTA = floor.read()
floor.close()

if str(FLOOR_DELTA) == '':
    FLOOR_DELTA = FLOOR_DELTA_STOCK

# define sensors for DHT and BMP
sensor_dht = Adafruit_DHT.DHT22
sensor_bmp = BMP085.BMP085()

def handle(msg):
    global SECURE
    global PASS
    global PASS_COUNT
    global SET_AIR_TEMP
    global AIR_TEMP
    global SET_FLOOR_DELTA
    global FLOOR_DELTA

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
        )
    elif command == '/set_air_temp':
        SET_AIR_TEMP = 1
        bot.sendMessage(chat_id, "Enter value")
    elif command == '/set_floor_delta':
        SET_FLOOR_DELTA = 1
        bot.sendMessage(chat_id, "Enter value")
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
        file_relay = open ('relay_switch', 'r')
        bot.sendMessage(chat_id,
        "RELAY STATUS: " + file_relay.read()
        + "\nDS_1 = " + str(DS_1) + " C"
        + "\nDS_2 = " + str(DS_2) + " C"
        + "\nBMP_PRESS = " + str(press_bmp) + " hg mm"
        + "\nBMP_TEMP = " + str(temp_bmp) + " C"
        + "\nDHT_H = " + str(humid_dht) + " %"
        + "\nDHT_T = " + str(temp_dht) + " C"
        + "\nFLOOR_DELTA = " + str(FLOOR_DELTA) + " C"
        + "\nAIR_TEMP = " + str(AIR_TEMP) + " C")
        file_relay.close()
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

def enable_relay():
    f = open('relay_switch', 'w')
    f.write('on')
    f.close()
def disable_relay():
    f = open('relay_switch', 'w')
    f.write('off')
    f.close()
def auto_relay():
    f = open('relay_switch', 'w')
    f.write('auto')
    f.close()
def write_floor_delta():
    global FLOOR_DELTA
    f = open(floor_delta_path, 'w')
    f.write(str(FLOOR_DELTA))
    f.close()
def write_air_temp():
    global AIR_TEMP
    f = open(air_temp_path, 'w')
    f.write(str(AIR_TEMP))
    f.close()

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)
