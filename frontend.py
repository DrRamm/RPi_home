#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import speech_recognition as sr
import pymorphy2
from pydub import AudioSegment

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

SET_HOURS = 0
SET_WEND_HOURS = 0

VOICE = 0

HOME_PATH = '/home/pi/'
air_and_floor_path = HOME_PATH + 'deltas'
relay_mode_path = HOME_PATH + 'relay_mode'
hours_path = HOME_PATH + 'hours'
hours_wend_path = HOME_PATH + 'hours_wend'
hours_mode_path = HOME_PATH + 'hours_mode'
all_values_path = HOME_PATH + 'all_values'
users_path = HOME_PATH + "users"

string_start = "\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s" % ( 
          "/get - получение информации: с датчиков, реле, по часам"
        , "/relay_on - Принудительное ВКЛючение реле"
        , "/relay_off - Принудительное ВЫКЛючение реле"
        , "/relay_auto - АВТОматический режим"
        , "/set_air_temp - Установка желаемой температуры воздуха"
        , "/set_floor_delta_min - Установка МИНИмальной дельты пола: разницы между подачей и обраткой. Служит для определения работы котла"
        , "/set_floor_delta_max - Установка МАКСИмальной дельты пола: разницы между подачей и обраткой. Служит для подогрева пола"
        , "/set_hours - Установка часов включения реле. Работает только когда реле в АВТОматическом режиме"
        , "/set_weekend_hours - Установка часов включения реле для выходного дня. Работает только когда реле в АВТОматическом режиме"
        , "/set_hours_on - ВКЛючение режима работы по часам"
        , "/set_hours_off - ВЫКЛючение режима работы по часам"
        , "/set_default_hours - Сброс часов на значения по умолчанию"
        , "/set_id_users")

def write_file(file_name, desired_value):
    f = open(file_name, 'w')
    f.write(str(desired_value))
    f.close()

def read_file(file_name):
    f = open(file_name, 'r')
    temp = f.read()
    f.close()
    return temp

def get_users():
    return read_file(users_path)

def write_users():
    write_file(users_path, ALLOWED_USERS)

def get_deltas():
    return read_file(air_and_floor_path)

def get_hours():
    return read_file(hours_path)

def get_hours_wend():
    return read_file(hours_wend_path)

def get_relay_mode():
    return read_file(relay_mode_path)

def get_hours_mode():
    return read_file(hours_mode_path)    
        
def get_values():
    BMP_T = 0
    BMP_P = 0
    DS_1 = 0
    DS_2 = 0
    DHT_H = 0
    DHT_T = 0
    RELAY_STATUS = 0

    FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX = get_deltas().split(" ")
        
    DS_1, DS_2, BMP_T, BMP_P, DHT_H, DHT_T, RELAY_STATUS = read_file(all_values_path).split(" ")
        
    values_string = "%s\n%s\n\n%s\n%s\n\n%s\n%s\n%s\n\n%s\n%s\n\n%s\n%s\n\n%s\n%s\n\n%s" % (
            "Режим реле (on|off|auto): %s"
        , "Текущее состояние реле (0|1) = %s"
        , "Температура обратки = %s C"
        , "Температура подачи = %s C"
        , "Текущая дельта пола = %s C"
        , "МИНИ дельта пола установлена = %s C"
        , "МАКСИ дельта пола установлена = %s C"
        , "Давление = %s мм.рт.ст"
        , "Влажноcть = %s %%"
        , "Средняя темп. воздуха = %s С"

        , "Желаемая темп. воздуха = %s С"
        , "Часы будние дни = %s"
        , "Часы выходные= %s"
        , "Режим работы по часам (on|off): %s")

    bot.sendMessage(chat_id, values_string % (
            get_hours_mode(), RELAY_STATUS, str(DS_1)[:5], str(DS_2)[:5], str(float(DS_2)-float(DS_1))[:5], 
            FLOOR_DELTA_MIN, FLOOR_DELTA_MAX, str(BMP_P)[:5], str(DHT_H)[:5], str((float(BMP_T) + float(DHT_T)) / 2)[:5], 
            AIR_TEMP, get_hours(), get_hours_wend(), get_hours_mode()))

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

def write_deltas(FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX):
    write_file(air_and_floor_path, "%s %s %s" % (FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX))
    bot.sendMessage(chat_id,
            "Максимальная дельта пола для срабатывания: %s\nМинимальная дельта пола для срабатывания: %s\nЖелаемая температура возудха: %s"
            % (FLOOR_DELTA_MAX, FLOOR_DELTA_MIN, AIR_TEMP))
        
def write_hours(HOURS):
    write_file(hours_path, HOURS)
    bot.sendMessage(chat_id, "Часы работы реле в будние: \n%s" %HOURS)

def write_wend_hours(HOURS_WEND):
    write_file(hours_wend_path, HOURS_WEND)
    bot.sendMessage(chat_id, "Часы работы реле в выходные: \n%s" % HOURS_WEND)

def set_default_hours():
    HOURS_STOCK = '1 3 5 6 7 13 16 18 19 20 22'
    HOURS_STOCK_WEND = '1 3 5 6 7 9 14 15 16 17 18 19 20 22'
    
    write_hours(HOURS_STOCK)
    write_wend_hours(HOURS_STOCK_WEND)

def normalization(norm_string):

    morph = pymorphy2.MorphAnalyzer()

    norm_string = norm_string.lower()
    norm_string = norm_string.split(" ")
    temp_list = []

    for temp in norm_string:
        temp = temp.decode('utf-8')
        temp_morph = morph.parse(temp)[0]
        temp_morph = temp_morph.normal_form
        temp_list.append(temp_morph)    

    return temp_list

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

    auto_words = 'Авто Автоматически Автоматический Автомат Само'
    auto_words = normalization(auto_words)

    relay_words = 'Пол Реле Релюху Этаж Отопление'
    relay_words = normalization(relay_words)

    is_initiated = 1

    print "Init done"

def make_good(data):
    enable_stuff = 4
    is_word_relay = 0

    normalized_data = normalization(data.encode('utf-8'))

    for temp in normalized_data: # Parse data

        if temp == "" or temp == " ":
            break

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
                break

        for temp_enable_words in enable_words: # Enable
            if (temp == temp_enable_words):
                enable_stuff = 1
                break

        for temp_auto_words in auto_words: # Auto
            if (temp == temp_auto_words):
                enable_stuff = 3
                break

        for temp_relay_words in relay_words: # relay
            if (temp == temp_relay_words):
                is_word_relay = 1
                break

    # Let's do smtng
    if (is_word_relay == 1):
        if (enable_stuff == 0):
            disable_relay()
        elif (enable_stuff == 1):
            enable_relay()
        elif (enable_stuff == 3):
            auto_relay()
        else:
            bot.sendMessage(chat_id, 'Не совсем понял про реле. Возможно, такое слово я не знаю')

def handle(msg):
    global SET_USERS
    global WRONG_ATTEMPTS

    global SET_AIR_TEMP
    global SET_FLOOR_DELTA_MIN
    global SET_FLOOR_DELTA_MAX

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

    ALLOWED_USERS = get_users()
    ALLOWED_USERS = ALLOWED_USERS.split(" ")
    for temp in ALLOWED_USERS:
        if str(chat_id) != str(temp) and int(chat_id) != 61099099:
            if WRONG_ATTEMPTS < 2 :
                print msg['from']['id']
                bot.sendMessage(chat_id, "Неверный id %s" % msg['from']['id'])
                WRONG_ATTEMPTS += 1
            elif WRONG_ATTEMPTS == 2:
                bot.sendMessage(chat_id, 'Эй, дружище, займись чем-нибудь другим')
            return

    if VOICE == 1:
        bot.download_file(msg['voice']['file_id'], HOME_PATH +  'voice.ogg')
        ogg_audio = AudioSegment.from_ogg(HOME_PATH + 'voice.ogg')
        ogg_audio.export(HOME_PATH + "voice.wav", format = "wav")
        r = sr.Recognizer()
        with sr.AudioFile(HOME_PATH + "voice.wav") as source:
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
        set_default_hours()
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
        if SET_AIR_TEMP == 1 or SET_FLOOR_DELTA_MIN == 1 or SET_FLOOR_DELTA_MAX == 1:
            FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX = get_deltas().split(" ")
            if SET_AIR_TEMP == 1:
                SET_AIR_TEMP = 0
                AIR_TEMP = command.encode('utf-8')

            if SET_FLOOR_DELTA_MIN == 1:
                SET_FLOOR_DELTA_MIN = 0
                FLOOR_DELTA_MIN = command.encode('utf-8')

            if SET_FLOOR_DELTA_MAX == 1:
                SET_FLOOR_DELTA_MAX = 0
                FLOOR_DELTA_MAX = command.encode('utf-8')
                
            write_deltas(FLOOR_DELTA_MIN, AIR_TEMP, FLOOR_DELTA_MAX)

        elif SET_HOURS == 1:
            SET_HOURS = 0
            write_hours(command.encode('utf-8'))

        elif SET_WEND_HOURS == 1:
            SET_WEND_HOURS = 0
            write_wend_hours(command.encode('utf-8'))

        elif SET_USERS == 1:
            SET_USERS = 0
            ALLOWED_USERS = command
            write_users()
            bot.sendMessage(chat_id, "Пользователи теперь такие - %s " % ALLOWED_USERS)
        else:
            markup = ReplyKeyboardMarkup(keyboard=[['/get'],[ '/start']])
            bot.sendMessage(chat_id, 'Горячие клавиши', reply_markup=markup)

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'
initial_strings()

while 1:
    time.sleep(4)
