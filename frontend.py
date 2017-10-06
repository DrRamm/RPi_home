import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

ALLOWED_USERS = ['61099099']
WRONG_ATTEMPTS = 0

SET_AIR_TEMP = 0
SET_FLOOR_DELTA = 0
AIR_TEMP_STOCK = 23
FLOOR_DELTA_STOCK = 1.5

HOURS_STOCK = '1 3 5 6 7 13 16 18 19 20 22'
SET_HOURS = 0

#values
BMP_T = 0
BMP_P = 0
DS_1 = 0
DS_2 = 0
DHT_H = 0
DHT_T = 0
RELAY_STATUS = 0

# modes
RELAY_MODE = ""
HOURS_MODE = ""

air_and_floor_path = 'deltas'
relay_mode_path = 'relay_mode'
hours_path = 'hours'
hours_mode_path = 'hours_mode'
all_values_path = 'all_values'

ds_1_path = '/sys/bus/w1/devices/28-0516814060ff/w1_slave'
ds_2_path = '/sys/bus/w1/devices/28-05169410e9ff/w1_slave'

try:
    air_and_floor = open(air_and_floor_path)
except:
    air_and_floor = open (air_and_floor_path, 'w')
    air_and_floor.write(str(AIR_TEMP_STOCK) + " " + str(FLOOR_DELTA_STOCK))
try:
    hours = open(hours_path)
except:
    hours = open(hours_path, 'w')
    hours.write(str(HOURS_STOCK))

temp_stuff=air_and_floor.read()
HOURS = hours.read()

hours.close()
air_and_floor.close()

FLOOR_DELTA,AIR_TEMP = temp_stuff.split(" ")

if str(AIR_TEMP) == "":
    AIR_TEMP = AIR_TEMP_STOCK

if str(FLOOR_DELTA) == '':
    FLOOR_DELTA = FLOOR_DELTA_STOCK

if str(HOURS) == '':
    HOURS = HOURS_STOCK

def get_hours():
    global HOURS

    f = open(hours_path, 'r')
    HOURS = f.read()
    f.close()

def get_modes():
    global RELAY_MODE
    global HOURS_MODE

    f = open(relay_mode_path, 'r')
    RELAY_MODE = f.read()
    f.close()

    f = open(hours_mode_path, 'r')
    HOURS_MODE = f.read()
    f.close()

def get_values():
    global BMP_T
    global BMP_P
    global DS_1
    global DS_2
    global DHT_H
    global DHT_T
    global RELAY_STATUS

    get_modes()
    get_hours()

    f = open(all_values_path, 'r')
    temp_stuff = f.read()
    DS_1, DS_2, BMP_T, BMP_P, DHT_H, DHT_T, RELAY_STATUS = temp_stuff.split(" ")
    f.close()

def enable_relay():
    f = open(relay_mode_path, 'w')
    f.write('on')
    f.close()

def disable_relay():
    f = open(relay_mode_path, 'w')
    f.write('off')
    f.close()

def auto_relay():
    f = open(relay_mode_path, 'w')
    f.write('auto')
    f.close()

def set_hours_off():
    f = open(hours_mode_path, 'w')
    f.write('off')
    f.close()

def set_hours_on():
    f = open(hours_mode_path, 'w')
    f.write('on')
    f.close()

def write_deltas():
    f = open(air_and_floor_path, 'w')
    f.write(str(FLOOR_DELTA) + " " + str(AIR_TEMP))
    f.close()

def write_hours():
    f = open(hours_path, 'w')
    f.write(str(HOURS))
    f.close()

def handle(msg):
    global WRONG_ATTEMPTS

    global SET_AIR_TEMP
    global AIR_TEMP

    global SET_FLOOR_DELTA
    global FLOOR_DELTA

    global HOURS
    global SET_HOURS

    chat_id = msg['chat']['id']
    command = msg['text']

    print 'Got command: %s' % command

    for temp in ALLOWED_USERS:
        if int(chat_id) != int(temp):
            if WRONG_ATTEMPTS < 2 :
                print msg['from']['username']
                print msg['from']['id']
                bot.sendMessage(chat_id, "Wrong user")
                WRONG_ATTEMPTS += 1
            elif WRONG_ATTEMPTS == 2:
                bot.sendMessage(chat_id, 'Hey, buddy, I think this stuff will suit you more than trying to use my bot')
                bot.sendPhoto(chat_id, 'http://pezik.com/gay/img/1/01.jpg', caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)
            return

    if command == '/start':
        markup = ReplyKeyboardMarkup(keyboard=[['/get', '/start']])
        bot.sendMessage(chat_id,
        "  /get - get status and values from sensors"
        + "\n\n /relay_on - Enable relay"
        + "\n\n /relay_off - Disable relay"
        + "\n\n /relay_auto - AUTO MODE"
        + "\n\n /set_air_temp - Set up AIR_TEMP"
        + "\n\n /set_floor_delta - Set up delta between grebyonka"
        + "\n\n /set_hours - Se up hours when relay will be enable in AUTO mode"
        + "\n\n /set_hours_on - Enable hours"
        + "\n\n /set_hours_off - Disable hours"
        + "\n\n /set_default_hours - reset all to default"
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
    elif command == '/set_hours_on':
        set_hours_on()
        bot.sendMessage(chat_id, "Hours Enabled")
    elif command == '/set_hours_off':
        set_hours_off()
        bot.sendMessage(chat_id, "Hours Disabled")
    elif command == '/set_default_hours':
        HOURS = HOURS_STOCK
        write_hours()
        bot.sendMessage(chat_id, "HOURS now are " + str(HOURS))
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
        bot.sendMessage(chat_id,
        "RELAY MODE: " + str(RELAY_MODE)
        + "\nRELAY STATUS = " + str(RELAY_STATUS)
        + "\n\nDS_1 = " + str(DS_1)[:5] + " C"
        + "\nDS_2 = " + str(DS_2)[:5] + " C"
        + "\nDS_2 - DS_1 = " + str(float(DS_2)-float(DS_1))
        + "\n\nBMP_PRESS = " + str(BMP_P)[:5] + " hg mm"
        + "\nBMP_TEMP = " + str(BMP_T)[:5] + " C"
        + "\n\nDHT_H = " + str(DHT_H)[:5] + " %"
        + "\nDHT_T = " + str(DHT_T)[:5] + " C"
        + "\n\nAVERAGE AIR TEMP = " + str((float(BMP_T) + float(DHT_T)) / 2)[:5] + " C"
        + "\n\nFLOOR_DELTA = " + str(float(FLOOR_DELTA)) + " C"
        + "\nAIR_TEMP = " + str(float(AIR_TEMP)) + " C"
        + "\nHOURS = " + str(HOURS)
        + "\nHOURS MODE:" + str(HOURS_MODE))
    else:
        markup = ReplyKeyboardMarkup(keyboard=[['/get'],[ '/start']])
        bot.sendMessage(chat_id, 'Lets go', reply_markup=markup)
        if SET_AIR_TEMP == 1:
            SET_AIR_TEMP = 0
            AIR_TEMP = command
            write_deltas()
            bot.sendMessage(chat_id, "AIR_TEMP now is " + str(AIR_TEMP))

        elif SET_FLOOR_DELTA == 1:
            SET_FLOOR_DELTA = 0
            FLOOR_DELTA = command
            write_deltas()
            bot.sendMessage(chat_id, "FLOOR_DELTA now is " + str(FLOOR_DELTA))

        elif SET_HOURS == 1:
            SET_HOURS = 0
            HOURS = command
            write_hours()
            bot.sendMessage(chat_id, "HOURS now are " + str(HOURS))

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(5)