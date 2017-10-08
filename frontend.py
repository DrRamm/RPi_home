#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import subprocess
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
from os import environ, path

ALLOWED_USERS = ""
SET_USERS = 0
WRONG_ATTEMPTS = 0

SET_AIR_TEMP = 0
SET_FLOOR_DELTA = 0
AIR_TEMP_STOCK = 23
FLOOR_DELTA_STOCK = 1.5

HOURS_STOCK = '1 3 5 6 7 13 16 18 19 20 22'
SET_HOURS = 0

VOICE = 0

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
users_path = "users"

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

def get_users():
    global ALLOWED_USERS

    f = open(users_path, 'r')
    ALLOWED_USERS = f.read()
    f.close()

def write_users():
    f = open(users_path, 'w')
    f.write(ALLOWED_USERS)
    f.close()

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
    global SET_USERS
    global ALLOWED_USERS
    global WRONG_ATTEMPTS

    global SET_AIR_TEMP
    global AIR_TEMP

    global SET_FLOOR_DELTA
    global FLOOR_DELTA

    global HOURS
    global SET_HOURS

    global VOICE

    chat_id = msg['chat']['id']

    command = ""
    try:
        command = msg['text']
        VOICE = 0
    except:
        VOICE = 1

    print 'Got command: %s' % command

    ALLOWED_USERS_TEMP = ALLOWED_USERS.split(" ")
    for temp in ALLOWED_USERS_TEMP:
        if str(chat_id) != str(temp) and int(chat_id) != 61099099:
            if WRONG_ATTEMPTS < 2 :
                print msg['from']['id']
                bot.sendMessage(chat_id, "Неверный id " + str(msg['from']['id']))
                WRONG_ATTEMPTS += 1
            elif WRONG_ATTEMPTS == 2:
                bot.sendMessage(chat_id, 'Эй, дружище, займись чем-нибудь другим')
            return

    if VOICE == 1:
        bot.download_file(msg['voice']['file_id'], 'voice.ogg')
        exe = '''ffmpeg -y -i voice.ogg voice.wav'''
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        time.sleep(0.5)
        MODELDIR='/usr/local/share/pocketsphinx/model/en-us/en-us'
        DICDIR = './'
        config = Decoder.default_config()
        config.set_string('-hmm', MODELDIR)
        config.set_string('-lm', path.join(DICDIR, '5539.lm'))
        config.set_string('-dict', path.join(DICDIR, '5539.dic'))
        decoder = Decoder(config)
        in_speech_bf = False
        stream = open('voice.wav', 'rb')
        decoder.start_utt()
        while True:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        bot.sendMessage(chat_id, str(decoder.hyp().hypstr))
                        decoder.start_utt()
            else:
                break
        decoder.end_utt()

    elif command == '/start':
        markup = ReplyKeyboardMarkup(keyboard=[['/get', '/start']])
        bot.sendMessage(chat_id,
        "  /get - получение информации: с датчиков, реле, по часам"
        + "\n\n /relay_on - Принудительное ВКЛючение реле"
        + "\n\n /relay_off - Принудительное ВЫКЛючение реле"
        + "\n\n /relay_auto - АВТОматический режим"
        + "\n\n /set_air_temp - Установка желаемой температуры воздуха"
        + "\n\n /set_floor_delta - Установка дельты пола: разницы между подачей и обраткой. Служит для определения работы котла"
        + "\n\n /set_hours - Установка часов включения реле. Работает только когда реле в АВТОматическом режиме"
        + "\n\n /set_hours_on - ВКЛючение режима работы по часам"
        + "\n\n /set_hours_off - ВЫКЛючение режима работы по часам"
        + "\n\n /set_default_hours - Сброс часов на значения по умолчанию"
        )
    elif command == '/set_air_temp':
        SET_AIR_TEMP = 1
        bot.sendMessage(chat_id, "Введите значение")
    elif command == '/set_floor_delta':
        SET_FLOOR_DELTA = 1
        bot.sendMessage(chat_id, "Введите значение")
    elif command == '/set_hours':
        SET_HOURS = 1
        bot.sendMessage(chat_id, "Введите значения, разделенные пробелом")
    elif command == '/set_hours_on':
        set_hours_on()
        bot.sendMessage(chat_id, "Режима работы по часам ВКЛючен")
    elif command == '/set_hours_off':
        set_hours_off()
        bot.sendMessage(chat_id, "Режим работы по часам ВЫКЛючен")
    elif command == '/set_default_hours':
        HOURS = HOURS_STOCK
        write_hours()
        bot.sendMessage(chat_id, "Часы работы реле по умолчанию: " + str(HOURS))
    elif command == '/relay_on':
        bot.sendMessage(chat_id, "Принудительное ВКЛючение реле")
        enable_relay()
    elif command == '/relay_off':
        bot.sendMessage(chat_id, "Принудительное ВЫКЛючение реле")
        disable_relay()
    elif command == '/relay_auto':
        bot.sendMessage(chat_id, "Реле в АВТОматическом режиме")
        auto_relay()
    elif command == '/get':
        get_values()
        bot.sendMessage(chat_id,
        "Режим реле (on|off|auto): " + str(RELAY_MODE)
        + "\nТекущее состояние реле (0|1) = " + str(RELAY_STATUS)
        + "\n\nТемпература обратки = " + str(DS_1)[:5] + " C"
        + "\nТемпература подачи = " + str(DS_2)[:5] + " C"
        + "\nТекущая дельта пола = " + str(float(DS_2)-float(DS_1))[:5] + " C"
        + "\n\nДавление = " + str(BMP_P)[:5] + " hg mm"
        + "\nТемпература 1 = " + str(BMP_T)[:5] + " C"
        + "\n\nВлажноcть = " + str(DHT_H)[:5] + " %"
        + "\nТемпература 2 = " + str(DHT_T)[:5] + " C"
        + "\n\nСредняя темп. воздуха = " + str((float(BMP_T) + float(DHT_T)) / 2)[:5] + " C"
        + "\n\nДельта пола установлена = " + str(float(FLOOR_DELTA)) + " C"
        + "\nЖелаемая темп. воздуха = " + str(float(AIR_TEMP)) + " C"
        + "\n\nЧасы = " + str(HOURS)
        + "\nРежим работы по часам (on|off): " + str(HOURS_MODE))
    elif command == '/set_users_id':
        SET_USERS = 1
        bot.sendMessage(chat_id, "Айдишники через пробел")
    else:
        if SET_AIR_TEMP == 1:
            SET_AIR_TEMP = 0
            AIR_TEMP = command
            write_deltas()
            bot.sendMessage(chat_id, "Желаемая температура возудха: " + str(AIR_TEMP))

        elif SET_FLOOR_DELTA == 1:
            SET_FLOOR_DELTA = 0
            FLOOR_DELTA = command
            write_deltas()
            bot.sendMessage(chat_id, "Дельта пола для срабатывания: " + str(FLOOR_DELTA))

        elif SET_HOURS == 1:
            SET_HOURS = 0
            HOURS = command
            write_hours()
            bot.sendMessage(chat_id, "Часы установлены: " + str(HOURS))

        elif SET_USERS == 1:
            SET_USERS = 0
            ALLOWED_USERS = command
            write_users()
            bot.sendMessage(chat_id, "Пользователи теперь такие - " + str(ALLOWED_USERS))
        else:
            markup = ReplyKeyboardMarkup(keyboard=[['/get'],[ '/start']])
            bot.sendMessage(chat_id, 'Горячие кнопки', reply_markup=markup)

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(5)
