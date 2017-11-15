#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import subprocess
from os import environ, path
import speech_recognition as sr

ALLOWED_USERS = ""
SET_USERS = 0
WRONG_ATTEMPTS = 0

SET_AIR_TEMP = 0
SET_FLOOR_DELTA_MIN = 0
SET_FLOOR_DELTA_MAX = 0
AIR_TEMP_STOCK = 23
FLOOR_DELTA_MIN_STOCK = 1.5
FLOOR_DELTA_MIN = 0
FLOOR_DELTA_MAX_STOCK = 11
FLOOR_DELTA_MAX = 0
AIR_TEMP = 0

HOURS_STOCK = '1 3 5 6 7 13 16 18 19 20 22'
HOURS_STOCK_WEND = '1 3 5 6 7 9 14 15 16 17 18 19 20 22'
SET_HOURS = 0
SET_WEND_HOURS = 0

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

HOME_PATH = '/home/pi/'
air_and_floor_path = HOME_PATH + 'deltas'
relay_mode_path = HOME_PATH + 'relay_mode'
hours_path = HOME_PATH + 'hours'
hours_wend_path = HOME_PATH + 'hours_wend'
hours_mode_path = HOME_PATH + 'hours_mode'
all_values_path = HOME_PATH + 'all_values'
users_path = HOME_PATH + "users"

ds_1_path = '/sys/bus/w1/devices/28-0516814060ff/w1_slave'
ds_2_path = '/sys/bus/w1/devices/28-05169410e9ff/w1_slave'

def get_users():
    global ALLOWED_USERS

    f = open(users_path, 'r')
    ALLOWED_USERS = f.read()
    f.close()

def write_users():
    f = open(users_path, 'w')
    f.write(ALLOWED_USERS)
    f.close()

def get_deltas():
    global FLOOR_DELTA_MIN
    global FLOOR_DELTA_MAX
    global AIR_TEMP
    f = open(air_and_floor_path, 'r')
    temp_stuff = f.read()
    FLOOR_DELTA_MIN,AIR_TEMP, FLOOR_DELTA_MAX = temp_stuff.split(" ")
    f.close()

def get_hours():
    global HOURS
    global HOURS_WEND

    f = open(hours_path, 'r')
    HOURS = f.read()
    f.close()

    f = open(hours_wend_path, 'r')
    HOURS_WEND = f.read()
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
    get_deltas()

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
    f.write(str(FLOOR_DELTA_MIN) + " " + str(AIR_TEMP) + " " + str(FLOOR_DELTA_MAX))
    f.close()

def write_hours():
    f = open(hours_path, 'w')
    f.write(str(HOURS))
    f.close()

def write_wend_hours():
    f = open(hours_wend_path, 'w')
    f.write(str(HOURS_WEND))
    f.close()

def handle(msg):
    global SET_USERS
    global ALLOWED_USERS
    global WRONG_ATTEMPTS

    global SET_AIR_TEMP
    global AIR_TEMP

    global SET_FLOOR_DELTA_MIN
    global FLOOR_DELTA_MIN
    global SET_FLOOR_DELTA_MAX
    global FLOOR_DELTA_MAX

    global HOURS
    global HOURS_WEND
    global SET_HOURS
    global SET_WEND_HOURS

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
        r = sr.Recognizer()
        time.sleep (2)
        with sr.AudioFile("voice.wav") as source:
                audio = r.record(source)
        try:
            recognized_text = r.recognize_google(audio, language="ru-RU")
            bot.sendMessage(chat_id, 'Вы сказали: ' + recognized_text.encode('utf-8'))
        except sr.UnknownValueError:
            bot.sendMessage(chat_id, "Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            bot.sendMessage(chat_id, "Could not request results from Google Speech Recognition service; {0}".format(e))

    elif command == '/start':
        markup = ReplyKeyboardMarkup(keyboard=[['/get', '/start']])
        bot.sendMessage(chat_id,
        "  /get - получение информации: с датчиков, реле, по часам"
        + "\n\n /relay_on - Принудительное ВКЛючение реле"
        + "\n\n /relay_off - Принудительное ВЫКЛючение реле"
        + "\n\n /relay_auto - АВТОматический режим"
        + "\n\n /set_air_temp - Установка желаемой температуры воздуха"
        + "\n\n /set_floor_delta_min - Установка МИНИмальной дельты пола: разницы между подачей и обраткой. Служит для определения работы котла"
        + "\n\n /set_floor_delta_max - Установка МАКСИмальной дельты пола: разницы между подачей и обраткой. Служит для подогрева пола"
        + "\n\n /set_hours - Установка часов включения реле. Работает только когда реле в АВТОматическом режиме"
        + "\n\n /set_weekend_hours - Установка часов включения реле для выходного дня. Работает только когда реле в АВТОматическом режиме"
        + "\n\n /set_hours_on - ВКЛючение режима работы по часам"
        + "\n\n /set_hours_off - ВЫКЛючение режима работы по часам"
        + "\n\n /set_default_hours - Сброс часов на значения по умолчанию"
        + "\n\n/set_id_users"
        )
    elif command == '/set_air_temp':
        SET_AIR_TEMP = 1
        bot.sendMessage(chat_id, "Введите значение")
    elif command == '/set_floor_delta_min':
        SET_FLOOR_DELTA_MIN = 1
        bot.sendMessage(chat_id, "Введите значение")
    elif command == '/set_floor_delta_max':
        SET_FLOOR_DELTA_MAX = 1
        bot.sendMessage(chat_id, "Введите значение")
    elif command == '/set_hours':
        SET_HOURS = 1
        bot.sendMessage(chat_id, "Введите значения, разделенные пробелом")
    elif command == '/set_weekend_hours':
        SET_WEND_HOURS = 1
        bot.sendMessage(chat_id, "Введите значения, разделенные пробелом")
    elif command == '/set_hours_on':
        set_hours_on()
        bot.sendMessage(chat_id, "Режима работы по часам ВКЛючен")
    elif command == '/set_hours_off':
        set_hours_off()
        bot.sendMessage(chat_id, "Режим работы по часам ВЫКЛючен")
    elif command == '/set_default_hours':
        HOURS = HOURS_STOCK
        HOURS_WEND = HOURS_WEND_STOCK
        write_hours()
        write_wend_hours()
        bot.sendMessage(chat_id, "Часы работы реле в будний: " + str(HOURS))
        bot.sendMessage(chat_id, "Часы работы реле в выходной: " + str(HOURS_WEND))
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
        + "\n\nТекущая дельта пола = " + str(float(DS_2)-float(DS_1))[:5] + " C"
        + "\nМИНИ дельта пола установлена = " + str(float(FLOOR_DELTA_MIN)) + " C"
        + "\nМАКСИ дельта пола установлена = " + str(float(FLOOR_DELTA_MAX)) + " C"
        + "\n\nДавление = " + str(BMP_P)[:5] + " hg mm"
        + "\nВлажноcть = " + str(DHT_H)[:5] + " %"
        + "\n\nСредняя темп. воздуха = " + str((float(BMP_T) + float(DHT_T)) / 2)[:5] + " C"

        + "\nЖелаемая темп. воздуха = " + str(float(AIR_TEMP)) + " C"
        + "\n\nЧасы будние дни = " + str(HOURS)
        + "\nЧасы выходные= " + str(HOURS_WEND)
        + "\n\nРежим работы по часам (on|off): " + str(HOURS_MODE))
    elif command == '/set_id_users':
        SET_USERS = 1
        bot.sendMessage(chat_id, "Айдишники через пробел")
    else:
        if SET_AIR_TEMP == 1:
            SET_AIR_TEMP = 0
            AIR_TEMP = command
            write_deltas()
            bot.sendMessage(chat_id, "Желаемая температура возудха: " + str(AIR_TEMP))

        elif SET_FLOOR_DELTA_MIN == 1:
            SET_FLOOR_DELTA_MIN = 0
            FLOOR_DELTA_MIN = command
            write_deltas()
            bot.sendMessage(chat_id, "Минимальная дельта пола для срабатывания: " + str(FLOOR_DELTA_MIN))
            
        elif SET_FLOOR_DELTA_MAX == 1:
            SET_FLOOR_DELTA_MAX = 0
            FLOOR_DELTA_MAX = command
            write_deltas()
            bot.sendMessage(chat_id, "Максимальная дельта пола для срабатывания: " + str(FLOOR_DELTA_MAX))

        elif SET_HOURS == 1:
            SET_HOURS = 0
            HOURS = command
            write_hours()
            bot.sendMessage(chat_id, "Часы установлены: " + str(HOURS))

        elif SET_WEND_HOURS == 1:
            SET_WEND_HOURS = 0
            HOURS_WEND = command
            write_wend_hours()
            bot.sendMessage(chat_id, "Часы для выходных установлены: " + str(HOURS_WEND))

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
