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
import pymorphy2

ALLOWED_USERS = ""
SET_USERS = 0
WRONG_ATTEMPTS = 0

chat_id = ""

is_initiated = 0
hi_words = ""
show_words = ""
enable_words = ""
disable_words = ""
auto_words = ""
relay_words = ""

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

string_start = ("  /get - получение информации: с датчиков, реле, по часам"
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
        + "\n\n/set_id_users")

def write_file(file, value):
    f = open(file, 'w')
    f.write(str(value))
    f.close()
    
def read_file(file):
    f = open(file, 'r')
    temp = f.read()
    f.close()
    return temp

def get_users():
    global ALLOWED_USERS
    ALLOWED_USERS = read_file(users_path)

def write_users():
    write_file(users_path, ALLOWED_USERS)

def get_deltas():
    global FLOOR_DELTA_MIN
    global FLOOR_DELTA_MAX
    global AIR_TEMP

    temp_stuff = read_file(air_and_floor_path)
    FLOOR_DELTA_MIN,AIR_TEMP, FLOOR_DELTA_MAX = temp_stuff.split(" ")

def get_hours():
    global HOURS
    global HOURS_WEND

    HOURS = read_file(hours_path)
    HOURS_WEND = read_file(hours_wend_path)

def get_modes():
    global RELAY_MODE
    global HOURS_MODE

    RELAY_MODE = read_file(relay_mode_path)
    HOURS_MODE = read_file(hours_mode_path)


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

    temp_stuff = read_file(all_values_path)
    DS_1, DS_2, BMP_T, BMP_P, DHT_H, DHT_T, RELAY_STATUS = temp_stuff.split(" ")
    
    bot.sendMessage(chat_id, "Режим реле (on|off|auto): " + str(RELAY_MODE)
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

def enable_relay():
    write_file(relay_mode_path, 'on')
    bot.sendMessage(chat_id, "Принудительное ВКЛючение реле")

def disable_relay():
    write_file(relay_mode_path, 'off')
    bot.sendMessage(chat_id, "Принудительное ВЫКЛючение реле")

def auto_relay():
    write_file(relay_mode_path, 'auto')
    bot.sendMessage(chat_id, "Реле в АВТОматическом режиме")

def set_hours_off():
    write_file(hours_mode_path, 'off')    
    bot.sendMessage(chat_id, "Режим работы по часам ВЫКЛючен")

def set_hours_on():
    write_file(hours_mode_path, 'on')
    bot.sendMessage(chat_id, "Режима работы по часам ВКЛючен")

def write_deltas():
    write_file(air_and_floor_path, str(FLOOR_DELTA_MIN) + " " + str(AIR_TEMP) + " " + str(FLOOR_DELTA_MAX))
    bot.sendMessage(chat_id, "Максимальная дельта пола для срабатывания: " + str(FLOOR_DELTA_MAX)
                   + "\nМинимальная дельта пола для срабатывания: " + str(FLOOR_DELTA_MIN)
                   + "\nЖелаемая температура возудха: " + str(AIR_TEMP))

def write_hours():
    write_file(hours_path, HOURS)
    bot.sendMessage(chat_id, "Часы работы реле в будние: " + str(HOURS))

def write_wend_hours():
    write_file(hours_wend_path, HOURS_WEND)
    bot.sendMessage(chat_id, "Часы работы реле в выходные: " + str(HOURS_WEND))

def normalization(norm_string):
    
    morph = pymorphy2.MorphAnalyzer()
    
    norm_string = norm_string.lower()      
    norm_string = norm_string.split(" ")
    temp_string = ""

    for temp in norm_string:        
        temp = temp.decode('utf-8') 
        temp_morph = morph.parse(temp)[0]
        temp_morph = temp_morph.normal_form        
        temp_string += temp_morph + " "
    
    print temp_string
    return temp_string.split(" ")

def initial_strings():
    global hi_words
    global show_words
    global enable_words
    global disable_words
    global auto_words
    global relay_words

    global is_initiated
    
    if (is_initiated == 1):
        return
    
    hi_words = 'Привет Здарова Здравствуй День Приветули Хай Хей-хо' 
    hi_words = normalization(hi_words)

    show_words = 'Покажи Состояние Статус Текущие Параметры Отобрази Запили Информация Инфа' 
    show_words = normalization(show_words)
    
    enable_words = 'Включи Вруби Зафигачь' 
    enable_words = normalization(enable_words)
    
    disable_words = 'Выключи Выруби Отключи Отруби' 
    disable_words = normalization(disable_words)
    
    auto_words = 'Авто Автоматический Автомат Само' 
    auto_words = normalization(auto_words)
    
    relay_words = 'Пол Реле Релюху Этаж Отопление' 
    relay_words = normalization(relay_words)
   
    is_initiated = 1
    
def make_good(data):
    
    initial_strings()
    
    enable_stuff = 4
    is_word_relay = 0

    normalized_data = normalization(data.encode('utf-8'))   
    
    for temp in normalized_data: # Parse data

        for temp_hi_words in hi_words: # Hi
            if (temp == temp_hi_words):                
                bot.sendMessage(chat_id, u'Привет, вот что я могу:')
                bot.sendMessage(chat_id, string_start)
                return
                
        for temp_show_words in show_words: # Show
            if (temp == temp_show_words):
                get_values()                  
                return
            
        for temp_disable_words in disable_words: # Disable
            if (temp == temp_disable_words):
                enable_stuff = 0                   
                return
            
        for temp_enable_words in enable_words: # Enable
            if (temp == temp_enable_words):
                enable_stuff = 1                   
                return
            
        for temp_auto_words in auto_words: # Auto
            if (temp == temp_auto_words):
                enable_stuff = 3                   
                return
            
        for temp_relay_words in relay_words: # relay
            if (temp == temp_relay_words):
                is_word_relay = 1                   
                return
    
    # Let's do smtng
    if (is_word_relay == 1):
        if (enable_stuff == 0):
            disable_relay()
        elif (enable_stuff == 1):
            enable_relay()
        elif (enable_stuff == 3):
            auto_relay()
        else:
            bot.sendMessage(chat_id, 'Не совсем понял про реле')
        

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
    
    global chat_id

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
        time.sleep(2)
        with sr.AudioFile("voice.wav") as source:
                audio = r.record(source)
        try:
            recognized_text = r.recognize_google(audio, language="ru-RU")
            bot.sendMessage(chat_id, 'Вы сказали: ' + recognized_text.encode('utf8'))
            make_good(recognized_text)
        except sr.UnknownValueError:
            bot.sendMessage(chat_id, u"Гугл не понимает тебя")
        except sr.RequestError as e:
            bot.sendMessage(chat_id, "Could not request results from Google Speech Recognition service; {0}".format(e))

    elif command == '/start':
        markup = ReplyKeyboardMarkup(keyboard=[['/get', '/start']])
        bot.sendMessage(chat_id, string_start)
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
    elif command == '/set_hours_off':
        set_hours_off()
    elif command == '/set_default_hours':
        HOURS = HOURS_STOCK
        HOURS_WEND = HOURS_WEND_STOCK
        write_hours()
        write_wend_hours()          
    elif command == '/relay_on':
        enable_relay()
    elif command == '/relay_off':        
        disable_relay()
    elif command == '/relay_auto':
        auto_relay()
    elif command == '/get':
        get_values()
    elif command == '/set_id_users':
        SET_USERS = 1
        bot.sendMessage(chat_id, "Айдишники через пробел")
    else:
        if SET_AIR_TEMP == 1:
            SET_AIR_TEMP = 0
            AIR_TEMP = command
            write_deltas()

        elif SET_FLOOR_DELTA_MIN == 1:
            SET_FLOOR_DELTA_MIN = 0
            FLOOR_DELTA_MIN = command
            write_deltas()
            
        elif SET_FLOOR_DELTA_MAX == 1:
            SET_FLOOR_DELTA_MAX = 0
            FLOOR_DELTA_MAX = command
            write_deltas()            

        elif SET_HOURS == 1:
            SET_HOURS = 0
            HOURS = command
            write_hours()            

        elif SET_WEND_HOURS == 1:
            SET_WEND_HOURS = 0
            HOURS_WEND = command
            write_wend_hours()

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
