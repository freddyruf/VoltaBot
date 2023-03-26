import json
import re
from pyrogram import filters
from dettails import api_hash 
from dettails import api_id

from keyboards import tastiera
from keyboards import tastiera2
from keyboards import tastiera3
from keyboards import tastiera4
from keyboards import allKeyboard


import tgcrypto
import random
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from pyrogram import Client


bot = Client("my_account", api_id=api_id, api_hash=api_hash)

def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")   #JSON file loaded
        return json.load(bot_responses)


# Store JSON data
response_data = load_json("bot.json")

import speech_recognition as sr
recognizer_instance = sr.Recognizer()
from pyttsx3 import init



import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re


risposta = ""

#function to find the type of message
def get_response(input_string):
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())
    score_list = []

    # Check all the responses
    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]

        # Check if there are any required words
        if required_words:
            for word in split_message:
                if word in required_words:
                    required_score += 1

        # Amount of required words should match the required score
        if required_score == len(required_words):
            # print(required_score == len(required_words))
            # Check each word the user has typed
            for word in split_message:
                # If the word is in the response, add to the score
                if word in response["user_input"]:
                    response_score += 1

        # Add score to list
        score_list.append(response_score)
        # Debugging: Find the best phrase
        # print(response_score, response["user_input"])

    # Find the best response and return it if they're not all 0
    best_response = max(score_list)
    response_index = score_list.index(best_response)

    # Check if input is empty
    if input_string == "":
        return -1

    # If there is no good response, return a random one.
    if best_response != 0:
        rt = ["", ""]
        rt[0] = response_data[response_index]["bot_response"]
        rt[1] = response_data[response_index]["response_type"]
        return rt

    return "Puoi ripetere?"


# {{{ creating connection
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,             #host values / *modify* if you not need to connect into a local host*
            passwd="root",

            database="test"  #database name / *modify*
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred when we try to connect into db")
    return connection
connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor() #cursor /Read-only attribute describing the result of a query.


tastiera=tastiera
tastiera2=tastiera2
tastiera3=tastiera3         #keyboards
tastiera4=tastiera4
allKeyboard=allKeyboard


def addLog(message):  # function to add the log into the database
    global cursor
    global connection
    global feedbot
    global feedresponse
    global feedmessage

    now = datetime.now()
    # Ottenere la data attuale come stringa nel formato 'YYYY-MM-DD'
    date_str = now.strftime('%Y-%m-%d')

    # Ottenere l'ora attuale come stringa nel formato 'HH:MM:SS'
    time_str = now.strftime('%H:%M:%S')

    timeinfo = date_str + " " + time_str  # time info

    cursor.execute(
        f"INSERT INTO log (tempo, usertext, requestinfo, responsetext) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}');")

    connection.commit()  # commit the changes


def addLogInfo(message, response, risposta):  # function to prepare the log into the database
    global feedbot
    global feedresponse
    global feedmessage

    feedmessage = message
    feedresponse = response
    feedbot = risposta

def prof_info(msg,orario,giorno): #function to get the info about the professor
    global cursor
    global risposta
    cursor.execute(f"SELECT ID FROM professori WHERE Nome = '{msg}'")
    PROF_ID = cursor.fetchall()  # id prof

    PROF_ID = PROF_ID[0][0]
    currentDateTime = datetime.now()  # actual date and time


    if(giorno == -1):
        Giorno = currentDateTime.isoweekday()  # day of the week
    else:
        Giorno = giorno
    if (Giorno == 1):
        Giorno = "orarioproflunedì"
    elif (Giorno == 2):
        Giorno = "orarioprofmartedì"
    elif (Giorno == 3):
        Giorno = "orarioprofmercoledì"
    elif (Giorno == 4):
        Giorno = "orarioprofgiovedì"
    elif (Giorno == 5):
        Giorno = "orarioprofvenerdì"
    else:
        engine.say("Giorno sbagliato!")
        risposta = "Giorno sbagliato!"
        engine.runAndWait()
        return 0

    #ciaoo
    if(orario == -1):
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario

    Ora -= 7              #indent for the database
    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
        engine.say("Ora sbagliata!")
        risposta = "Ora sbagliata!"
        engine.runAndWait()
        return 0
    if (Ora == 1):
        Ora = "primaOra"
    elif (Ora == 2):
        Ora = "secondaOra"
    elif (Ora == 3):
        Ora = "terzaOra"
    elif (Ora == 4):
        Ora = "quartaOra"
    elif (Ora == 5):
        Ora = "quintaOra"
    elif (Ora == 6):
        Ora = "sestaOra"
    elif (Ora == 7):
        Ora = "settimaOra"
    elif (Ora == 8):
        Ora = "ottavaOra"



    cursor.execute(f"SELECT {Ora} FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
    Classe = cursor.fetchall()  # class found
    Classe = Classe[0][0]
    if(Classe=="libero" or Classe=="Libero"):   #control if the professor is free all hours
        cursor.execute(f"SELECT primaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        prima = cursor.fetchall()

        cursor.execute(f"SELECT secondaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        seconda = cursor.fetchall()

        cursor.execute(f"SELECT terzaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        terza = cursor.fetchall()

        cursor.execute(f"SELECT quartaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        quarta = cursor.fetchall()

        cursor.execute(f"SELECT quintaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        quinta = cursor.fetchall()

        cursor.execute(f"SELECT sestaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        sesta = cursor.fetchall()

        #control if the professor is free all hours
        if (prima[0][0]=="libero" and seconda[0][0]=="libero" and terza[0][0]=="libero" and quarta[0][0]=="libero" and quinta[0][0]=="libero" and sesta[0][0]=="libero"): return 2
        elif (prima[0][0]=="Libero" and seconda[0][0]=="Libero" and terza[0][0]=="Libero" and quarta[0][0]=="Libero" and quinta[0][0]=="Libero" and sesta[0][0]=="Libero"): return 2

        return 1 #only the hour


    cursor.execute(f"SELECT IDaula FROM classi WHERE classe = '{Classe}'") # id aula
    IDAula = cursor.fetchall()
    IDAula = IDAula[0][0]

    cursor.execute(f"SELECT Palazzina,Piano,Aula FROM aule WHERE ID ='{IDAula}'") # info aula
    Aula = cursor.fetchall()  # catch the info about the class
    Palazzina = Aula[0][0]
    Piano = Aula[0][1]
    nAula = Aula[0][2]
    result = [Palazzina,Piano,nAula]
    return result

def cerca_orario(str): #function to find the hour in the string
    str = re.split(' ', str.lower())
    tot = 0
    nulla=True
    for c in str:

        #in words
        if (c == "prima"):
            return 8
        elif (c == "seconda"):
            return 9
        elif (c == "terza"):
            return 10
        elif (c == "quarta"):
            return 11
        elif (c == "quinta"):
            return 12
        elif (c == "sesta"):
            return 13
        elif (c == "settima"):
            return 14
        elif (c == "ottava"):
            return 15

        #in numbers
        elif (ord(c[0]) > 47 and ord(c[0]) < 58):

            string = re.split(':', c)

            for i in string:

                if (len(i) == 2 and ord(i[1]) > 47 and ord(i[1]) < 58): #if the hour is in the format 00:00
                    nulla=False
                    tot = (ord(i[0]) - 48) * 10 + (ord(i[1]) - 48)
                    break
                elif("?" in i): #if the hour is in the format 0? or 0:00?
                    nulla = False
                    tot = ord(i[0]) - 48
                    break

                else: #if the hour is in the format 0
                    nulla=False
                    tot = ord(i[0]) - 48
                    break
    if(nulla): #not found
        return -1
    else:
        return tot #return the hour

#searching the name of the professor
def find2(str):
    str = re.split(' ', str.upper()) # split the string
    for c in str: #for each word
        for i in allKeyboard: #for each keyboard
            for z in i: #for each word in the keyboard
                if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in z): #if the word is in the keyboard
                    return z #return the name
    return 0


#searching the day
def cerca_giorno(str):
    str = re.split(' ', str.lower()) # split the string
    for c in str:
        if ("luned" in c):
            return 1
        elif ("marted" in c):
            return 2
        elif ("mercoled" in c):
            return 3
        elif ("gioved" in c):
            return 4
        elif ("venerd" in c):
            return 5
        elif ("sabato" in c):
            return 6
        elif ("domenica" in c):
            return 7
    return -1


engine= init()
voices=(engine.getProperty("voices"))
engine.setProperty('voice',voices[0].id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)  # Riduci la velocità di 50 unità
while True:
    recognizer_instance = sr.Recognizer()
    with sr.Microphone() as source:

        recognizer_instance.adjust_for_ambient_noise(source)
        print("Sono in ascolto parla pure..")
        audio = recognizer_instance.listen(source)
        print("Messaggio in elaborazione")
        try:
            text = recognizer_instance.recognize_google(audio, language="it-IT")

            response = get_response(text)  # get the response from the type of message requested
            type = response[1]  # get the type of message
            response = response[0]  # get the response
            temp = text  # save the message

            if (response == "trovato"):  # asking for a professor
                text = find2(text)  # modify the message text to the name of the professor (to work in some functions)

                if (text != 0):  # if the professor is found

                    ora = cerca_orario(temp)  # search the time

                    giorno = cerca_giorno(temp)  # search the day
                    info = prof_info(text,ora,giorno)  # get the info about the professor (ora and giorno can be '-1' if not found)
                    if (info == 1):
                        engine.say(f"Il prof {text.title()} è libero")  # if he is free
                        risposta = "Il prof è libero"
                        engine.runAndWait()
                    elif (info == 2):
                        engine.say(f"Il prof oggi non c'è a scuola")  # if he is not in school all time
                        risposta = "Il prof oggi non c'è a scuola"
                        engine.runAndWait()
                    elif (info != 0):
                        engine.say(f"Il prof {text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}")  # if he is in school
                        risposta = f"Il prof si trova in: Palazzina: {info[0]} Piano: {info[1]} Aula: {info[2]}"
                        engine.runAndWait()

                text = temp  # restore the message
            else:
                engine.say(response)  # send the response of message requested
                engine.runAndWait()
                risposta = response # save the response
            addLogInfo(text, type+" *audio* ", risposta)  # add the log
            addLog(text)  # add the log into db
        except Exception as e:
            print(e)


